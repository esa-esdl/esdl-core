
import math
import os
from collections import OrderedDict
from datetime import datetime, timedelta

import xarray as xr
from xarray import Dataset


class _CubeVar:
    def __init__(self, index, name, dir_path):
        self.index = index
        self.name = name
        self.dir_path = dir_path
        self.dataset = None


#: The names in this list are not *data* variables but *coordinate* variables.
EXTRA_COORDS_VAR_NAMES = ['time_bnds', 'lat_bnds', 'lon_bnds']


class CubeDataAccess:
    """
    Represents the cube's data (access).

    :param cube_config: A :py:class`CubeConfig` object.
    :param cube_base_dir: Base path to cube.
    """

    def __init__(self, cube_config, cube_base_dir):

        try:
            import dask
        except ImportError:
            print('WARNING: missing Python package "dask", expect runtime performance issues!')

        self._cube_config = cube_config

        self._cube_var_dict = OrderedDict()
        self._cube_var_list = []

        data_dir = os.path.join(cube_base_dir, 'data')
        data_dir_entries = sorted(os.listdir(data_dir))
        var_index = 0
        for data_dir_entry in data_dir_entries:
            var_dir = os.path.join(data_dir, data_dir_entry)
            if os.path.isdir(var_dir):
                var_name = data_dir_entry
                cube_var = _CubeVar(var_index, var_name, var_dir)
                self._cube_var_dict[var_name] = cube_var
                self._cube_var_list.append(cube_var)
                var_index += 1

    def __getitem__(self, key):
        """
        Same as ``variable(key=key)``.
        """
        return self._variable(key, False)

    def __iter__(self):
        return iter(self._cube_var_list)

    def __len__(self):
        return len(self._cube_var_list)

    @property
    def shape(self):
        """
        Return the shape of the data cube.
        """
        cube_config = self._cube_config
        year_1 = cube_config.start_time.year
        year_2 = cube_config.end_time.year
        years = year_2 - year_1
        if cube_config.end_time > datetime(cube_config.end_time.year, 1, 1):
            years += 1
        time_size = years * cube_config.num_periods_per_year
        return len(self._cube_var_list), time_size, cube_config.grid_height, cube_config.grid_width

    @property
    def variable_names(self) -> list:
        """
        Return a sequence of variable names in alphabetical order.
        """
        return [cube_var.name for cube_var in self._cube_var_list]

    def variable(self, key=None):
        """
        Get one or more cube variables as ``xarray.DataArray`` instances. Same as, e.g. ``cube.data['ozone']``.

        :param key: The variable selector, which can be a name, or index, or a sequence of names and indices.
                Valid names (type ``str``) are the ones returned by the ``variable_names`` list while valid
                indices (type ``int``) point into this list, which is in alphabetical order w.r.t. the variable names.
                If a sequence is provided, a sequence will be returned.
                Passing ``None`` is equivalent to passing the ``variable_names`` list.
        :return: a ``xarray.DataArray`` instance or a sequence of such representing the variable(s) with the
                dimensions (time, latitude, longitude).
        """
        return self._variable(key if key is not None else self.variable_names, True)

    def _variable(self, key, method_call):
        if isinstance(key, int):
            key = self._cube_var_list[key]
            dataset = self._get_or_open_dataset(key)
            return dataset.variables[key.name]
        elif isinstance(key, str):
            key = self._cube_var_dict[key]
            dataset = self._get_or_open_dataset(key)
            return dataset.variables[key.name]
        elif method_call or not isinstance(key, tuple):
            indices = self._get_var_indices(key)
            data_arrays = []
            for i in indices:
                key = self._cube_var_list[i]
                dataset = self._get_or_open_dataset(key)
                data_arrays.append(dataset.variables[key.name])
            return data_arrays
        else:
            raise IndexError('key cannot be a tuple')

    def dataset(self, key=None) -> xr.Dataset:
        """
        .. _xarray.Dataset: http://xarray.pydata.org/en/stable/data-structures.html#dataset

        Get one or more cube variables as a single `xarray.Dataset`_ with the dimensions (time, latitude, longitude).

        :param key: The variable selector, which can be a name, or index, or a sequence of names and indices.
                Valid names (type ``str``) are the ones returned by the ``variable_names`` list while valid
                indices (type ``int``) point into this list.
                If a sequence is provided, a sequence will be returned.
                Passing ``None`` is equivalent to passing the ``variable_names`` list.
        :return: an `xarray.Dataset`_ instance with the dimensions (time, latitude, longitude).
        """

        if isinstance(key, int):
            key = self._cube_var_list[key]
            return self._get_or_open_dataset(key)
        elif isinstance(key, str):
            key = self._cube_var_dict[key]
            return self._get_or_open_dataset(key)
        else:
            indices = self._get_var_indices(key)
            data_arrays = {}
            for i in indices:
                key = self._cube_var_list[i]
                dataset = self._get_or_open_dataset(key)
                # data_arrays[key.name] = dataset.variables[key.name]
                data_arrays = xr.merge([data_arrays, dataset])
            return xr.Dataset(data_arrays)

    # TODO (forman, 20160713): Remove method, add time, lat, lon to variable() and dataset()
    # TODO (forman, 20160713): Use xarray API to achieve the same result
    def get(self, variable=None, time=None, latitude=None, longitude=None):
        """
        Get the cube's data as a list of numpy-like data arrays. The returned list will 
        correspond to the **variable** argument. A one-element list will be returned
        even if **variable** is not a list.

        :param variable: an variable index or name or a sequence of variable indexes or names
        :param time: a single datetime.datetime object or a 2-element iterable (time_start, time_end)
        :param latitude: a single latitude value or a 2-element iterable (latitude_start, latitude_end)
        :param longitude: a single longitude value or a 2-element iterable (longitude_start, longitude_end)
        :return: a dictionary mapping variable names --> data arrays of dimension (time, latitude, longitude)
        """

        var_indexes = self._get_var_indices(variable)
        time_1, time_2 = self._get_time_range(time)
        lat_1, lat_2 = self._get_lat_range(latitude)
        lon_1, lon_2 = self._get_lon_range(longitude)

        config = self._cube_config
        time_index_1 = int(math.floor(
            ((time_1 - config.ref_time) / timedelta(days=config.temporal_res))))
        time_index_2 = int(math.floor(
            ((time_2 - config.ref_time) / timedelta(days=config.temporal_res))))
        grid_y1 = int(round((90.0 - lat_2) / (180 / config.grid_height))) - config.grid_y0
        grid_y2 = int(round((90.0 - lat_1) / (180 / config.grid_height))) - config.grid_y0
        grid_x1 = int(round((180.0 + lon_1) / (360 / config.grid_width))) - config.grid_x0
        grid_x2 = int(round((180.0 + lon_2) / (360 / config.grid_width))) - config.grid_x0

        if grid_y2 > grid_y1 and 90.0 - (grid_y2 + config.grid_y0) * (180 / config.grid_height) == lat_1:
            grid_y2 -= 1
        if grid_x2 > grid_x1 and -180.0 + (grid_x2 + config.grid_x0) * (360 / config.grid_width) == lon_2:
            grid_x2 -= 1

        global_grid_width = int(round(360.0 / config.spatial_res))
        dateline_intersection = grid_x2 >= global_grid_width

        if dateline_intersection:
            grid_x11 = grid_x1
            grid_x12 = global_grid_width - 1
            grid_x21 = 0
            grid_x22 = grid_x2
            # TODO (forman, 20151102) - Handle data requests intersecting the dateline, see issue #15
            print('dateline intersection! grid_x: %d-%d, %d-%d' %
                  (grid_x11, grid_x12, grid_x21, grid_x22))
            raise ValueError(
                'illegal longitude: %s: dateline intersection not yet implemented' % longitude)

        # TODO (forman, 20151102) - Fill in NaN, where a variable does not provide any data, see issue #17
        result = []
        # shape = time_index_2 - time_index_1 + 1, \
        #         grid_y2 - grid_y1 + 1, \
        #         grid_x2 - grid_x1 + 1
        for var_index in var_indexes:
            variable = self.variable(var_index)
            # result += [numpy.full(shape, numpy.NaN, dtype=numpy.float32)]
            # print('variable.shape =', variable.shape)
            array = variable[slice(time_index_1, time_index_2 + 1) if (time_index_1 < time_index_2) else time_index_1,
                             slice(grid_y1, grid_y2 + 1) if (grid_y1 < grid_y2) else grid_y1,
                             slice(grid_x1, grid_x2 + 1) if (grid_x1 < grid_x2) else grid_x1]
            result += [array]
        return result

    def close(self):
        """
        Close cube data access by closing all open files it might be referring to.
        """
        self._close_datasets()

    def _get_lon_range(self, longitude):
        if longitude is None:
            return -180, 180
        try:
            # Try using longitude as longitude pair
            lon_1, lon_2 = longitude
        except TypeError:
            # Longitude scalar
            lon_1 = longitude
            lon_2 = longitude
        # Adjust longitude to -180..+180
        if lon_1 < -180:
            lon_1 %= 180
        if lon_1 > 180:
            lon_1 %= -180
        if lon_2 < -180:
            lon_2 %= 180
        if lon_2 > 180:
            lon_2 %= -180
        # If lon_1 > lon_2 --> dateline intersection, add 360 so that lon_1 < lon_2
        if lon_1 > lon_2:
            lon_2 += 360
        return lon_1, lon_2

    def _get_lat_range(self, latitude):
        if latitude is None:
            return -90, 90
        try:
            # Try using latitude as latitude pair
            lat_1, lat_2 = latitude
        except TypeError:
            # Latitude scalar
            lat_1 = latitude
            lat_2 = latitude
        if lat_1 < -90 or lat_1 > 90 or lat_2 < -90 or lat_2 > 90 or lat_1 > lat_2:
            raise ValueError('invalid latitude argument: %s' % latitude)
        return lat_1, lat_2

    def _get_time_range(self, time):
        if time is None:
            return self._cube_config.start_time, self._cube_config.end_time
        try:
            # Try using time as time pair
            time_1, time_2 = time
        except TypeError:
            # Time scalar
            time_1 = time
            time_2 = time
        if time_1 > time_2:
            raise ValueError('invalid time argument: %s' % time)
        return time_1, time_2

    def _get_var_indices(self, variable):
        if variable is None:
            return range(len(self._cube_var_list))
        try:
            # Try using variable as string name
            var_index = self._cube_var_dict[variable].index
            return [var_index]
        except (KeyError, TypeError):
            try:
                # Try using variable as integer index
                _ = self._cube_var_list[variable]
                return [variable]
            except (KeyError, TypeError):
                # Try using variable as iterable of name and/or indexes
                var_indexes = []
                for v in variable:
                    try:
                        # Try using v as string name
                        var_index = self._cube_var_dict[v].index
                        var_indexes += [var_index]
                    except (KeyError, TypeError):
                        try:
                            # Try using v as integer index
                            _ = self._cube_var_list[v]
                            var_index = v
                            var_indexes += [var_index]
                        except (KeyError, TypeError):
                            raise ValueError('illegal variable argument: %s' % variable)
                return var_indexes

    def _get_or_open_dataset(self, cube_var):
        if not cube_var.dataset:
            self._open_dataset(cube_var)
        return cube_var.dataset

    def _open_dataset(self, variable):
        file_pattern = os.path.join(variable.dir_path, '*.nc')
        chunk_sizes = self._cube_config.chunk_sizes
        dask_chunks = None
        if chunk_sizes:
            time_size, lat_size, lon_size = chunk_sizes
            # TODO (forman): use multiples of chunk sizes in certain dimensions
            #                until some constraint is fulfilled.
            #                e.g. hint that allows using max. XYZ MB per variable,
            #                only have multiples in time dimension, because users want
            #                time-series analysis...
            dask_chunks = dict(time=time_size, lat=lat_size, lon=lon_size)
        variable.dataset = xr.open_mfdataset(file_pattern,
                                             concat_dim='time',
                                             preprocess=self._preprocess_dataset,
                                             engine='h5netcdf',
                                             chunks=dask_chunks,
                                             data_vars='minimal')

    def _preprocess_dataset(self, ds: Dataset):
        # Convert specific data variables to coordinate variables
        for var_name in EXTRA_COORDS_VAR_NAMES:
            if var_name in ds.data_vars:
                ds.set_coords(var_name, inplace=True)
        # print(ds)
        return ds

    def _close_datasets(self):
        for cube_var in self._cube_var_list:
            if cube_var.dataset:
                cube_var.dataset.close()
                cube_var.dataset = None
