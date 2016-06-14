import math
import os
from collections import OrderedDict
from datetime import datetime, timedelta

import netCDF4

import cablab
import cablab.util
from .cube_config import CubeConfig, __version__
from .cube_provider import CubeSourceProvider


class Cube:
    """
    Represents a data cube. Use the static **open()** or **create()** methods to obtain data cube objects.
    """

    def __init__(self, base_dir, config):
        self._base_dir = base_dir
        self._config = config
        self._closed = False
        self._data = None

    def __repr__(self) -> str:
        return 'Cube(%s, \'%s\')' % (self._config, self._base_dir)

    @property
    def base_dir(self) -> str:
        """
        The cube's base directory.
        """
        return self._base_dir

    @property
    def config(self) -> CubeConfig:
        """
        The cube's configuration. See CubeConfig class.
        """
        return self._config

    def info(self) -> str:
        """
        Return a human-readable information string about this data cube (markdown formatted).
        """
        # todo (nf 20151104) - read from data cube's dir, see issue #5
        return ''

    @property
    def closed(self):
        """
        Checks if the cube has been closed.
        """
        return self._closed

    @property
    def data(self):
        """
        The cube's data. See **CubeData** class.
        """
        if not self._data:
            self._data = CubeData(self)
        return self._data

    @staticmethod
    def open(base_dir):
        """
        Open an existing data cube. Use the **Cube.update(provider)** method to add data to the cube
        via a source data provider.

        :param base_dir: The data cube's base directory which must be empty or non-existent.
        :return: A cube instance.
        """

        if not os.path.exists(base_dir):
            raise IOError('data cube base directory does not exists: %s' % base_dir)
        config = CubeConfig.load(os.path.join(base_dir, 'cube.config'))
        return Cube(base_dir, config)

    @staticmethod
    def create(base_dir, config=CubeConfig()):
        """
        Create a new data cube. Use the **Cube.update(provider)** method to add data to the cube
        via a source data provider.

        :param base_dir: The data cube's base directory. Must not exists.
        :param config: The data cube's static information.
        :return: A cube instance.
        """

        if os.path.exists(base_dir):
            raise IOError('data cube base directory exists: %s' % base_dir)
        os.mkdir(base_dir)
        config.store(os.path.join(base_dir, 'cube.config'))
        return Cube(base_dir, config)

    def close(self):
        """
        Closes the data cube.
        """
        if self._data:
            self._data.close()
            self._data = None
        self._closed = True

    def update(self, provider: CubeSourceProvider):
        """
        Updates the data cube with source data from the given image provider.

        :param provider: An instance of the abstract ImageProvider class
        """
        if self._closed:
            raise IOError('cube has been closed')

        provider.prepare()
        target_start_time, target_end_time = provider.temporal_coverage
        if self._config.start_time and self._config.start_time > target_start_time:
            target_start_time = self._config.start_time
        if self._config.end_time and self._config.end_time < target_end_time:
            target_end_time = self._config.end_time
        target_year_1 = target_start_time.year
        target_year_2 = target_end_time.year
        cube_temporal_res = self._config.temporal_res
        num_periods_per_year = self._config.num_periods_per_year
        datasets = dict()


        for target_year in range(target_year_1, target_year_2 + 1):
            time_min = datetime(target_year, 1, 1)
            time_max = datetime(target_year + 1, 1, 1)
            d_time = timedelta(days=cube_temporal_res)
            time_1 = time_min
            for key in datasets:
                if (target_year-1 == int(key[0:4])):
                    datasets[key].close()
            for time_index in range(num_periods_per_year):
                time_2 = time_1 + d_time
                if time_2 > time_max:
                    time_2 = time_max
                weight = cablab.util.temporal_weight(time_1, time_2, target_start_time, target_end_time)
                if weight > 0.0:
                    var_name_to_image = provider.compute_variable_images(time_1, time_2)
                    if var_name_to_image:
                        self._write_images(provider, datasets, (time_index, time_1, time_2), var_name_to_image)
                time_1 = time_2
        provider.close()

    def _write_images(self, provider, datasets, target_time, var_name_to_image):
        for var_name in var_name_to_image:
            image = var_name_to_image[var_name]
            if image is not None:
                self._write_image(provider, datasets, target_time, var_name, image)

    def _write_image(self, provider, datasets, target_time, var_name, image):
        time_index, target_start_time, target_end_time = target_time
        folder_name = var_name
        folder = os.path.join(os.path.join(self._base_dir, 'data', folder_name))
        if not os.path.exists(folder):
            os.makedirs(folder, exist_ok=True)
        filename = '%04d_%s.nc' % (target_start_time.year, var_name)
        file = os.path.join(folder, filename)
        if filename in datasets:
            dataset = datasets[filename]
        else:
            if os.path.exists(file):
                dataset = netCDF4.Dataset(file, 'a')
            else:
                dataset = netCDF4.Dataset(file, 'w', format=self._config.file_format)
                self._init_variable_dataset(provider, dataset, var_name, target_start_time.year)
            datasets[filename] = dataset

        t2 = self._config.date2num(target_end_time)
        var_time = dataset.variables['time']
        time_bnds = dataset.variables['time_bnds']
        if time_bnds[time_index,1] != t2:
            print("Warning: Time stamps discrepancy: %f is is not %f" %( time_bnds[time_index,1],t2 ))
            print("target start: %s, target end %s" % (target_start_time, target_end_time))

        var_variable = dataset.variables[var_name]
        var_variable[time_index, :, :] = image

    def _init_variable_dataset(self, provider, dataset, variable_name, start_year):
        import time

        # todo (nf 20160512) - some of these attributes could be read from cube configuration
        # see http://cfconventions.org/cf-conventions/v1.6.0/cf-conventions.html#description-of-file-contents
        # see http://cfconventions.org/cf-conventions/v1.6.0/cf-conventions.html#attribute-appendix
        dataset.Conventions = 'CF-1.6'
        dataset.institution = 'Brockmann Consult GmbH, Germany'
        dataset.source = 'CAB-LAB data cube generation, version %s' % __version__
        dataset.history = time.ctime(time.time()) + ' - CAB-LAB data cube generation'
        #
        # check (nf 20151023) - add more global attributes from CF-conventions here,
        #                       especially those that reference original sources and originators
        #
        # dataset.title = ...
        # dataset.references = ...
        # dataset.comment = ...

        dataset.northing = '%s degrees' % self.config.northing
        dataset.easting = '%s degrees' % self.config.easting
        dataset.spatial_res = '%s degrees' % self.config.spatial_res

        image_x0, image_y0, image_width, image_height = provider.spatial_coverage

        dataset.createDimension('bnds', 2)
        dataset.createDimension('time', self._config.num_periods_per_year)
        dataset.createDimension('lat', image_height)
        dataset.createDimension('lon', image_width)

        var_time_bnds = dataset.createVariable('time_bnds', 'f8', ('time', 'bnds'), fill_value=-9999.0)
        var_time_bnds.units = self._config.time_units
        var_time_bnds.calendar = self._config.calendar
        var_time_bnds[:,0] = [self._config.date2num(datetime(start_year,1,1,0,0)) + self._config.temporal_res*(i+0.) for i in range(self._config.num_periods_per_year)]
        upper_bounds = [self._config.date2num(datetime(start_year,1,1,0,0)) + self._config.temporal_res*(i+1.0) for i in range(self._config.num_periods_per_year)]
        upper_bounds[-1] = self._config.date2num(datetime(start_year+1,1,1,0,0))
        var_time_bnds[:,1] = upper_bounds

        var_time = dataset.createVariable('time', 'f8', ('time',), fill_value=-9999.0)
        var_time.long_name = 'time'
        var_time.standard_name = 'time'
        var_time.units = self._config.time_units
        var_time.calendar = self._config.calendar
        var_time.bounds = 'time_bnds'
        times = [self._config.date2num(datetime(start_year,1,1,0,0)) + self._config.temporal_res*(i+0.5) for i in range(self._config.num_periods_per_year)]
        #times[-1] = var_time_bnds[-1,0] + (var_time_bnds[-1,1] - var_time_bnds[-1,0]) / 2.
        # Thus, we keep date of the last time range always at Julian day 364, not in the center of the period.
        # The time bounds then specify the real extent of the period.
        # Uncomment the upper line to center it between the upper and lower bound!
        var_time[:] = times

        var_longitude = dataset.createVariable('lon', 'f4', ('lon',))
        var_longitude.long_name = 'longitude'
        var_longitude.standard_name = 'longitude'
        var_longitude.units = 'degrees_east'
        var_longitude.bounds = 'lon_bnds'

        var_longitude_bnds = dataset.createVariable('lon_bnds', 'f4', ('lon', 'bnds'))
        var_longitude_bnds.units = 'degrees_east'

        var_latitude = dataset.createVariable('lat', 'f4', ('lat',))
        var_latitude.long_name = 'latitude'
        var_latitude.standard_name = 'latitude'
        var_latitude.units = 'degrees_north'
        var_latitude.bounds = 'lat_bnds'

        var_latitude_bnds = dataset.createVariable('lat_bnds', 'f4', ('lat', 'bnds'))
        var_latitude_bnds.units = 'degrees_north'

        spatial_res = self._config.spatial_res

        lon0 = self._config.easting + image_x0 * spatial_res
        for i in range(image_width):
            lon = lon0 + i * spatial_res
            var_longitude[i] = lon + 0.5 * spatial_res
            var_longitude_bnds[i,0] = lon
            var_longitude_bnds[i,1] = lon + spatial_res

        lat0 = self._config.northing + image_y0 * spatial_res
        for i in range(image_height):
            lat = lat0 - i * spatial_res
            var_latitude[i] = lat - 0.5 * spatial_res
            var_latitude_bnds[i,0] = lat - spatial_res
            var_latitude_bnds[i,1] = lat

        variable_descriptors = provider.variable_descriptors
        variable_attributes = variable_descriptors[variable_name]
        # Mandatory attributes
        variable_data_type = variable_attributes['data_type']
        variable_fill_value = variable_attributes['fill_value']
        var_variable = dataset.createVariable(variable_name, variable_data_type,
                                              ('time', 'lat', 'lon',),
                                              zlib=self._config.compression,
                                              fill_value=variable_fill_value)
        var_variable.scale_factor = variable_attributes.get('scale_factor', 1.0)
        var_variable.add_offset = variable_attributes.get('add_offset', 0.0)

        # Set remaining NetCDF attributes
        for name in variable_attributes:
            if name not in {'data_type', 'fill_value', 'scale_factor', 'add_offset'}:
                value = variable_attributes[name]
                try:
                    var_variable.__setattr__(name, value)
                except ValueError as ve:
                    # todo (nf 20160512) - log, or print to stderr
                    print('%s = %s failed (%s)!' % (name, value, str(ve)))
        return dataset

    @staticmethod
    def _get_num_steps(x1, x2, dx):
        return int(math.floor((x2 - x1) / dx))


class CubeData:
    """
    Represents the cube's read-only data.

    :param cube: A **Cube** object.
    """

    def __init__(self, cube):
        self._cube = cube
        self._dataset_files = []
        self._var_index_to_var_name = OrderedDict()
        self._var_name_to_var_index = OrderedDict()
        data_dir = os.path.join(cube.base_dir, 'data')
        data_dir_entries = os.listdir(data_dir)
        var_index = 0
        for data_dir_entry in data_dir_entries:
            var_dir = os.path.join(data_dir, data_dir_entry)
            if os.path.isdir(var_dir):
                var_name = data_dir_entry
                var_dir_entries = os.listdir(var_dir)
                var_dir_entries = [var_dir_entry for var_dir_entry in var_dir_entries if var_dir_entry.endswith('.nc')]
                var_dir_entries = sorted(var_dir_entries)
                var_dir_entries = [os.path.join(var_dir, var_dir_entry) for var_dir_entry in var_dir_entries]
                self._var_index_to_var_name[var_index] = var_name
                self._var_name_to_var_index[var_name] = var_index
                self._dataset_files.append(var_dir_entries)
                var_index += 1
        self._datasets = [None] * len(self._dataset_files)
        self._variables = [None] * len(self._dataset_files)

    @property
    def shape(self) -> tuple:
        """
        Return the shape of the data cube.
        """
        year_1 = self._cube.config.start_time.year
        year_2 = self._cube.config.end_time.year
        years = year_2 - year_1
        if self._cube.config.end_time > datetime(self._cube.config.end_time.year, 1, 1):
            years += 1
        time_size = years * self._cube.config.num_periods_per_year
        return len(self._dataset_files), time_size, self._cube.config.grid_height, self._cube.config.grid_width

    @property
    def variable_names(self) -> tuple:
        """
        Return a dictionary of variable names to indices.
        """
        return dict(self._var_name_to_var_index)

    def get_variable(self, var_index):
        """
        Get a cube variable. Same as, e.g. ``cube.data['Ozone']``.

        :param var_index: The variable name or index according to the list returned by the ``variable_names`` property.
        :return: a data-access object representing the variable with the dimensions (time, latitude, longitude).
        """
        if isinstance(var_index, str):
            var_index = self._var_name_to_var_index[var_index]
        return self._get_or_open_variable(var_index)

    def get_dataset(self, var_index):
        """
        Get the dataset associated with a cube variable.

        :param var_index: The variable name or index according to the list returned by the ``variable_names`` property.
        :return: a data-access object representing the variable with the dimensions (time, latitude, longitude).
        """
        if isinstance(var_index, str):
            var_index = self._var_name_to_var_index[var_index]
        return self._datasets[var_index] if 0 <= var_index < len(self._datasets) else None

    def __getitem__(self, index):
        """
        Get a cube variable. Same as, e.g. ``cube.data.get_variable('Ozone')``.

        :param index: The variable name or index according to the list returned by the ``variable_names`` property.
        :return: a data-access object representing the variable with the dimensions (time, latitude, longitude).
        """
        return self.get_variable(index)

    def get(self, variable=None, time=None, latitude=None, longitude=None):
        """
        Get the cube's data.

        :param variable: an variable index or name or an iterable returning multiple of these (var1, var2, ...)
        :param time: a single datetime.datetime object or a 2-element iterable (time_start, time_end)
        :param latitude: a single latitude value or a 2-element iterable (latitude_start, latitude_end)
        :param longitude: a single longitude value or a 2-element iterable (longitude_start, longitude_end)
        :return: a dictionary mapping variable names --> data arrays of dimension (time, latitude, longitude)
        """

        var_indexes = self._get_var_indices(variable)
        time_1, time_2 = self._get_time_range(time)
        lat_1, lat_2 = self._get_lat_range(latitude)
        lon_1, lon_2 = self._get_lon_range(longitude)

        config = self._cube.config
        time_index_1 = int(math.floor(((time_1 - config.ref_time) / timedelta(days=config.temporal_res))))
        time_index_2 = int(math.floor(((time_2 - config.ref_time) / timedelta(days=config.temporal_res))))
        grid_y1 = int(round((90.0 - lat_2) / config.spatial_res)) - config.grid_y0
        grid_y2 = int(round((90.0 - lat_1) / config.spatial_res)) - config.grid_y0
        grid_x1 = int(round((180.0 + lon_1) / config.spatial_res)) - config.grid_x0
        grid_x2 = int(round((180.0 + lon_2) / config.spatial_res)) - config.grid_x0

        if grid_y2 > grid_y1 and 90.0 - (grid_y2 + config.grid_y0) * config.spatial_res == lat_1:
            grid_y2 -= 1
        if grid_x2 > grid_x1 and -180.0 + (grid_x2 + config.grid_x0) * config.spatial_res == lon_2:
            grid_x2 -= 1

        global_grid_width = int(round(360.0 / config.spatial_res))
        dateline_intersection = grid_x2 >= global_grid_width

        if dateline_intersection:
            grid_x11 = grid_x1
            grid_x12 = global_grid_width - 1
            grid_x21 = 0
            grid_x22 = grid_x2
            # todo (nf 20151102) - Handle data requests intersecting the dateline, see issue #15
            print('dateline intersection! grid_x: %d-%d, %d-%d' % (grid_x11, grid_x12, grid_x21, grid_x22))
            raise ValueError('illegal longitude: %s: dateline intersection not yet implemented' % longitude)

        # todo (nf 20151102) - Fill in NaN, where a variable does not provide any data, see issue #17
        result = []
        # shape = time_index_2 - time_index_1 + 1, \
        #         grid_y2 - grid_y1 + 1, \
        #         grid_x2 - grid_x1 + 1
        for var_index in var_indexes:
            variable = self._get_or_open_variable(var_index)
            # result += [numpy.full(shape, numpy.NaN, dtype=numpy.float32)]
            # print('variable.shape =', variable.shape)
            array = variable[slice(time_index_1, time_index_2 + 1) if (time_index_1 < time_index_2) else time_index_1,
                             slice(grid_y1, grid_y2 + 1) if (grid_y1 < grid_y2) else grid_y1,
                             slice(grid_x1, grid_x2 + 1) if (grid_x1 < grid_x2) else grid_x1]
            result += [array]
        return result

    def close(self):
        """
        Closes this **CubeData** by closing all open datasets.
        """
        self._close_datasets()

    @staticmethod
    def _get_lon_range(longitude):
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

    @staticmethod
    def _get_lat_range(latitude):
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
            return self._cube.config.start_time, self._cube.config.end_time
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
            return self._var_index_to_var_name.keys()
        try:
            # Try using variable as string name
            var_index = self._var_name_to_var_index[variable]
            return [var_index]
        except (KeyError, TypeError):
            try:
                # Try using variable as integer index
                _ = self._var_index_to_var_name[variable]
                return [variable]
            except (KeyError, TypeError):
                # Try using variable as iterable of name and/or indexes
                var_indexes = []
                for v in variable:
                    try:
                        # Try using v as string name
                        var_index = self._var_name_to_var_index[v]
                        var_indexes += [var_index]
                    except (KeyError, TypeError):
                        try:
                            # Try using v as integer index
                            _ = self._var_index_to_var_name[v]
                            var_index = v
                            var_indexes += [var_index]
                        except (KeyError, TypeError):
                            raise ValueError('illegal variable argument: %s' % variable)
                return var_indexes

    def _get_or_open_variable(self, var_index):
        if self._variables[var_index]:
            return self._variables[var_index]
        return self._open_dataset(var_index)

    def _open_dataset(self, var_index):
        files = self._dataset_files[var_index]
        var_name = self._var_index_to_var_name[var_index]
        dataset = netCDF4.MFDataset(files, aggdim='time')
        variable = dataset.variables[var_name]
        self._datasets[var_index] = dataset
        self._variables[var_index] = variable
        return variable

    def _close_datasets(self):
        for i in range(len(self._datasets)):
            dataset = self._datasets[i]
            dataset.close()
            self._datasets[i] = None
            self._variables[i] = None
