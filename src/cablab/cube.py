import math
import os
import time
from abc import ABCMeta, abstractmethod, abstractproperty
from collections import OrderedDict
from datetime import datetime, timedelta

import gridtools.resampling as gtr
import netCDF4
import numpy as np

import cablab
import cablab.util
from .util import NetCDFDatasetCache, aggregate_images, temporal_weight

# The current version of the data cube's configuration and data model.
CUBE_MODEL_VERSION = '0.1'


class CubeSourceProvider(metaclass=ABCMeta):
    """
    An abstract interface for objects representing data source providers for the data cube.
    Cube source providers are passed to the **Cube.update()** method.

    :param cube_config: Specifies the fixed layout and conventions used for the cube.
    :param name: The provider's registration name.
    """

    def __init__(self, cube_config, name):
        if not cube_config:
            raise ValueError('cube_config expected')
        if not name:
            raise ValueError('name expected')
        self._name = name
        self._cube_config = cube_config

    @property
    def name(self) -> str:
        """ The provider's registration name. """
        return self._name

    @property
    def cube_config(self):
        """ The data cube's configuration. """
        return self._cube_config

    @abstractmethod
    def prepare(self):
        """
        Called by a Cube instance's **update()** method before any other provider methods are called.
        Provider instances should prepare themselves w.r.t. the given cube configuration *cube_config*.
        """
        pass

    @abstractproperty
    def temporal_coverage(self) -> tuple:
        """
        Return the start and end time of the available source data.

        :return: A tuple of datetime.datetime instances (start_time, end_time).
        """
        return None

    @abstractproperty
    def spatial_coverage(self) -> tuple:
        """
        Return the spatial coverage as a rectangle represented by a tuple of integers (x, y, width, height) in the
        cube's image coordinates.

        :return: A tuple of integers (x, y, width, height) in the cube's image coordinates.
        """
        return None

    @abstractproperty
    def variable_descriptors(self) -> dict:
        """
        Return a variable name to variable descriptor mapping of all provided variables.
        Each descriptor is a dictionary of variable attribute names to their values.
        The attributes ``data_type`` (a numpy data type) and ``fill_value`` are mandatory.


        :return: dictionary of variable names to attribute dictionaries
        """
        # todo - describe new resamping options here, see gridtools.resampling.DS_xxx and US_xx
        return None

    @abstractmethod
    def compute_variable_images(self, period_start, period_end) -> dict:
        """
        Return variable name to variable image mapping of all provided variables.
        Each image is a numpy array with the shape (height, width) derived from the **get_spatial_coverage()** method.

        The images must be computed (by aggregation or interpolation or copy) from the source data in the given
        time period *period_start* <= source_data_time < *period_end* and taking into account other data cube
        configuration settings.

        The method is called by a Cube instance's **update()** method for all possible time periods in the time
        range given by the **get_temporal_coverage()** method. The times given are adjusted w.r.t. the cube's
        reference time and temporal resolution.

        :param period_start: The period start time as a datetime.datetime instance
        :param period_end: The period end time as a datetime.datetime instance

        :return: A dictionary variable name --> image. Each image must be numpy array-like object of shape
                 (grid_height, grid_width) as given by the **CubeConfig**.
                 Return ``None`` if no such variables exists for the given target time range.
        """
        return None

    @abstractmethod
    def close(self):
        """
        Called by the cube's **update()** method after all images have been retrieved and the provider is no
        longer used.
        """
        pass


class BaseCubeSourceProvider(CubeSourceProvider):
    """
    A partial implementation of the **CubeSourceProvider** interface that computes its output image data
    using weighted averages. The weights are computed according to the overlap of source time ranges and a
    requested target time range.

    :param cube_config: Specifies the fixed layout and conventions used for the cube.
    :param name: The provider's registration name.
    """

    def __init__(self, cube_config, name):
        super(BaseCubeSourceProvider, self).__init__(cube_config, name)
        self._source_time_ranges = None

    def prepare(self):
        """
        Calls **compute_source_time_ranges** and assigns the return value to the field **source_time_ranges**.
        """
        self._source_time_ranges = self.compute_source_time_ranges()

    @property
    def source_time_ranges(self):
        return self._source_time_ranges

    @property
    def spatial_coverage(self):
        """
        Return the spatial grid coverage given in the Cube's configuration (default).

        :return: A tuple of integers (x, y, width, height) in the cube's image coordinates.
        """
        return 0, 0, self.cube_config.grid_width, self.cube_config.grid_height

    @property
    def temporal_coverage(self) -> (datetime, datetime):
        """
        Return the temporal coverage derived from the value returned by **compute_source_time_ranges()**.
        """
        return self._source_time_ranges[0][0], self._source_time_ranges[-1][1]

    @abstractmethod
    def compute_source_time_ranges(self) -> list:
        """
        Return a sorted list of all time ranges of every source file.
        Items in this list must be 4-element tuples of the form
        (time_start: datetime, time_stop: datetime, file: str, time_index: int).
        The method is called from the **prepare()** method in order to pre-compute all available time ranges.
        This method must be implemented by derived classes.
        """
        return None

    def compute_variable_images(self, period_start, period_end):
        """
        For each source time range that has an overlap with the given target time range compute a weight
        according to the overlapping range. Pass these weights as source index to weight mapping
        to **compute_variable_images_from_sources(index_to_weight)** and return the result.

        :return: A dictionary variable name --> image. Each image must be numpy array-like object of shape
                 (grid_height, grid_width) as given by the **CubeConfig**.
                 Return ``None`` if no such variables exists for the given target time range.
        """

        source_time_ranges = self._source_time_ranges
        if len(source_time_ranges) == 0:
            return None

        index_to_weight = dict()
        for i in range(len(source_time_ranges)):
            source_start_time, source_end_time = source_time_ranges[i][0:2]
            weight = temporal_weight(source_start_time, source_end_time,
                                     period_start, period_end)
            if weight > 0.0:
                index_to_weight[i] = weight
        if not index_to_weight:
            return None

        self.log('computing images for time range %s to %s from %d source(s)...' % (period_start, period_end,
                                                                                    len(index_to_weight)))
        t1 = time.time()
        result = self.compute_variable_images_from_sources(index_to_weight)
        t2 = time.time()
        self.log('images computed for %s, took %f seconds' % (str(list(result.keys())), t2 - t1))

        return result

    @abstractmethod
    def compute_variable_images_from_sources(self, index_to_weight):
        """
        Compute the target images for all variables from the sources with the given time indices to weights mapping.

        The time indices in *index_to_weight* are guaranteed to point into the time ranges list returned by
        **compute_source_time_ranges()**.

        The weight values in *index_to_weight* are float values computed from the overlap of source time ranges with
        a requested target time range.

        :param index_to_weight: A dictionary mapping time indexes --> weight values.
        :return: A dictionary variable name --> image. Each image must be numpy array-like object of shape
                 (grid_height, grid_width) as specified by the cube's layout configuration **CubeConfig**.
                 Return ``None`` if no such variables exists for the given target time range.
        """
        pass

    def log(self, message):
        """
        Log a *message*.

        :param message: The message to be logged.
        """
        print('%s: %s' % (self.name, message))

    def _get_file_and_time_index(self, var_index):
        """
        Return the file path and time dimension index as tuple.
        To be used by derived classes only.
        """
        return self._source_time_ranges[var_index][2:4]


class NetCDFCubeSourceProvider(BaseCubeSourceProvider):
    """
    A BaseCubeSourceProvider that
    * Uses NetCDF source datasets read from a given **dir_path**
    * Performs temporal aggregation first and then spatial resampling
    """

    def __init__(self, cube_config, name, dir_path):
        super(NetCDFCubeSourceProvider, self).__init__(cube_config, name)
        self._dir_path = dir_path
        self._dataset_cache = NetCDFDatasetCache(name)
        self._old_indices = None

    @property
    def name(self):
        return self._dir_path

    @property
    def dir_path(self):
        return self._dir_path

    @property
    def dataset_cache(self):
        return self._dataset_cache

    def compute_variable_images_from_sources(self, index_to_weight):

        # close all datasets that wont be used anymore
        new_indices = set(index_to_weight.keys())
        if self._old_indices:
            unused_indices = self._old_indices - new_indices
            for i in unused_indices:
                file, _ = self._get_file_and_time_index(i)
                self._dataset_cache.close_dataset(file)
        self._old_indices = new_indices

        var_descriptors = self.variable_descriptors
        target_var_images = dict()
        for var_name, var_attributes in var_descriptors.items():
            source_var_images = [None] * len(new_indices)
            source_weights = [None] * len(new_indices)
            var_image_index = 0
            for i in new_indices:
                file, time_index = self._get_file_and_time_index(i)
                variable = self._dataset_cache.get_dataset(file).variables[var_name]
                if len(variable.shape) == 3:
                    var_image = variable[time_index, :, :]
                elif len(variable.shape) == 2:
                    var_image = variable[:, :]
                else:
                    raise TypeError("unexpected shape for variable '%s'" % var_name)
                source_var_images[var_image_index] = var_image
                source_weights[var_image_index] = index_to_weight[i]
                var_image_index += 1
            if len(new_indices) > 1:
                # Temporal aggregation
                var_image = aggregate_images(source_var_images, weights=source_weights)
            else:
                # Temporal aggregation not required
                var_image = source_var_images[0]
            # Spatial resampling
            var_image = gtr.resample_2d(var_image,
                                        self.cube_config.grid_width,
                                        self.cube_config.grid_height,
                                        ds_method=gtr.__dict__['DS_' + var_attributes.get('ds_method', 'MEAN')],
                                        us_method=gtr.__dict__['US_' + var_attributes.get('us_method', 'NEAREST')],
                                        fill_value=var_attributes.get('fill_value', np.nan))
            target_var_images[var_name] = var_image

        return target_var_images

    def close(self):
        self._dataset_cache.close_all_datasets()


class TestCubeSourceProvider(CubeSourceProvider):
    def __init__(self,
                 cube_config,
                 name,
                 variable_name):
        super(TestCubeSourceProvider, self).__init__(cube_config, name)
        self._variable_name = variable_name
        self._start_time = datetime(2005, 1, 1)
        self._end_time = datetime(2006, 1, 1)
        self._value = 0.0

    def prepare(self):
        pass

    @property
    def temporal_coverage(self):
        return self._start_time, self._end_time

    @property
    def spatial_coverage(self):
        return 0, 0, self.cube_config.grid_width, self.cube_config.grid_height

    @property
    def variable_descriptors(self):
        return {
            self._variable_name: {
                'data_type': np.float32,
                'fill_value': np.nan,
                'scale_factor': 1.0,
                'add_offset': 0.0,
            }
        }

    def compute_variable_images(self, period_start, period_end):
        self._value += 0.1
        image_width = self.cube_config.grid_width
        image_height = self.cube_config.grid_height
        image_shape = (image_height, image_width)
        return {
            self._variable_name: np.full(image_shape, self._value, dtype=np.float32)
        }

    def close(self):
        pass


class CubeConfig:
    """
    A data cube's static configuration information.

    :param spatial_res: The spatial image resolution in degree.
    :param grid_x0: The fixed grid X offset (longitude direction).
    :param grid_y0: The fixed grid Y offset (latitude direction).
    :param grid_width: The fixed grid width in pixels (longitude direction).
    :param grid_height: The fixed grid height in pixels (latitude direction).
    :param temporal_res: The temporal resolution in days.
    :param ref_time: A datetime value which defines the units in which time values are given, namely
                     'days since *ref_time*'.
    :param start_time: The inclusive start time of the first image of any variable in the cube given as datetime value.
                       ``None`` means unlimited.
    :param end_time: The exclusive end time of the last image of any variable in the cube given as datetime value.
                     ``None`` means unlimited.
    :param variables: A list of variable names to be included in the cube.
    :param file_format: The file format used. Must be one of 'NETCDF4', 'NETCDF4_CLASSIC', 'NETCDF3_CLASSIC'
                        or 'NETCDF3_64BIT'.
    :param compression: Whether the data should be compressed.
    """

    def __init__(self,
                 spatial_res=0.25,
                 grid_x0=0,
                 grid_y0=0,
                 grid_width=1440,
                 grid_height=720,
                 temporal_res=8,
                 calendar='gregorian',
                 ref_time=datetime(2001, 1, 1),
                 start_time=datetime(2001, 1, 1),
                 end_time=datetime(2011, 1, 1),
                 variables=None,
                 file_format='NETCDF4_CLASSIC',
                 compression=False,
                 model_version=CUBE_MODEL_VERSION):
        self.model_version = model_version
        self.spatial_res = spatial_res
        self.grid_x0 = grid_x0
        self.grid_y0 = grid_y0
        self.grid_width = grid_width
        self.grid_height = grid_height
        self.temporal_res = temporal_res
        self.calendar = calendar
        self.ref_time = ref_time
        self.start_time = start_time
        self.end_time = end_time
        self.variables = variables
        self.file_format = file_format
        self.compression = compression
        self._validate()

    def __repr__(self):
        return 'CubeConfig(spatial_res=%f, grid_x0=%d, grid_y0=%d, grid_width=%d, grid_height=%d, ' \
               'temporal_res=%d, ref_time=%s)' % (
                   self.spatial_res,
                   self.grid_x0, self.grid_y0,
                   self.grid_width, self.grid_height,
                   self.temporal_res,
                   repr(self.ref_time))

    @property
    def northing(self):
        """
        The longitude position of the upper-left-most corner of the upper-left-most grid cell
        given by (grid_x0, grid_y0).
        """
        return 90.0 - self.grid_y0 * self.spatial_res

    @property
    def easting(self):
        """
        The latitude position of the upper-left-most corner of the upper-left-most grid cell
        given by (grid_x0, grid_y0).
        """
        return -180.0 + self.grid_x0 * self.spatial_res

    @property
    def geo_bounds(self):
        """
        The geographical boundary given as ((LL-lon, LL-lat), (UR-lon, UR-lat)).
        """
        return ((self.easting, self.northing - self.grid_height * self.spatial_res),
                (self.easting + self.grid_width * self.spatial_res, self.northing))

    @property
    def time_units(self):
        """
        Return the time units used by the data cube as string using the format 'days since *ref_time*'.
        """
        ref_time = self.ref_time
        return 'days since %4d-%02d-%02d %02d:%02d' % \
               (ref_time.year, ref_time.month, ref_time.day, ref_time.hour, ref_time.minute)

    @property
    def num_periods_per_year(self):
        """
        Return the number of target periods per year.
        """
        return math.ceil(365.0 / self.temporal_res)

    def date2num(self, date):
        """
        Return the number of days for the given *date* as a number in the time units
        given by the ``time_units`` property.

        :param date: The date as a datetime.datetime value
        """
        return netCDF4.date2num(date, self.time_units, calendar=self.calendar)

    @staticmethod
    def load(path):
        """
        Load a CubeConfig from a text file.

        :param path: The file's path name.
        :return: A new CubeConfig instance
        """
        config = dict()
        with open(path) as fp:
            code = fp.read()
            exec(code, {'datetime': __import__('datetime')}, config)

        CubeConfig._ensure_compatible_config(config)

        return CubeConfig(**config)

    @staticmethod
    def _ensure_compatible_config(config_dict):
        model_version = config_dict.get('model_version', None)
        # Here: check for compatibility with Cube.MODEL_VERSION, convert if possible, otherwise raise error.
        if model_version is None or model_version < CUBE_MODEL_VERSION:
            print('WARNING: outdated cube model version, current version is %s' % CUBE_MODEL_VERSION)

    def store(self, path):
        """
        Store a CubeConfig in a text file.

        :param path: The file's path name.
        """
        with open(path, 'w') as fp:
            for name in self.__dict__:
                if not (name.startswith('_') or name.endswith('_')):
                    value = self.__dict__[name]
                    fp.write('%s = %s\n' % (name, repr(value)))

    def _validate(self):
        if self.grid_x0 < 0:
            raise ValueError('illegal grid_x0 value')

        if self.grid_y0 < 0:
            raise ValueError('illegal grid_y0 value')

        lat1 = 90 - (self.grid_y0 + self.grid_height) * self.spatial_res
        lat2 = 90 - self.grid_y0 * self.spatial_res
        if lat1 >= lat2 or lat1 < -90 or lat1 > 90 or lat2 < -90 or lat2 > 90:
            raise ValueError('illegal combination of grid_y0, grid_height, spatial_res values')

        lon1 = -180 + self.grid_x0 * self.spatial_res
        lon2 = -180 + (self.grid_x0 + self.grid_width) * self.spatial_res
        if lon1 >= lon2 or lon1 < -180 or lon1 > 180 or lon2 < -180 or lon2 > 180:
            raise ValueError('illegal combination of grid_x0, grid_width, spatial_res values')


class Cube:
    """
    Represents a data cube. Use the static **open()** or **create()** methods to obtain data cube objects.
    """

    def __init__(self, base_dir, config):
        self._base_dir = base_dir
        self._config = config
        self._closed = False
        self._data = None

    def __repr__(self):
        return 'Cube(%s, \'%s\')' % (self._config, self._base_dir)

    @property
    def base_dir(self):
        """
        The cube's base directory.
        """
        return self._base_dir

    @property
    def config(self):
        """
        The cube's configuration. See CubeConfig class.
        """
        return self._config

    def info(self):
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

    def update(self, provider):
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
            for time_index in range(num_periods_per_year):
                time_2 = time_1 + d_time
                if time_2 > time_max:
                    time_2 = time_max
                weight = cablab.util.temporal_weight(time_1, time_2, target_start_time, target_end_time)
                # print('Period: %s to %s: %f' % (time_1, time_2, weight))
                if weight > 0.0:
                    var_name_to_image = provider.compute_variable_images(time_1, time_2)
                    if var_name_to_image:
                        self._write_images(provider, datasets, (time_index, time_1, time_2), var_name_to_image)
                time_1 = time_2

        for key in datasets:
            datasets[key].close()

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
                self._init_variable_dataset(provider, dataset, var_name)
            datasets[filename] = dataset

        t1 = self._config.date2num(target_start_time)
        t2 = self._config.date2num(target_end_time)

        var_time = dataset.variables['time']
        var_time[time_index] = t1 + 0.5 * (t2 - t1)

        var_time_bnds = dataset.variables['time_bnds']
        var_time_bnds[time_index, 0] = t1
        var_time_bnds[time_index, 1] = t2

        var_variable = dataset.variables[var_name]
        var_variable[time_index, :, :] = image

    def _init_variable_dataset(self, provider, dataset, variable_name):

        image_x0, image_y0, image_width, image_height = provider.spatial_coverage

        dataset.createDimension('bnds', 2)
        dataset.createDimension('time', self._config.num_periods_per_year)
        dataset.createDimension('lat', image_height)
        dataset.createDimension('lon', image_width)

        var_time = dataset.createVariable('time', 'f8', ('time',), fill_value=-9999.0)
        var_time.units = self._config.time_units
        var_time.calendar = self._config.calendar
        var_time.bounds = 'time_bnds'
        var_time[:] = -9999.0

        var_time_bnds = dataset.createVariable('time_bnds', 'f8', ('time', 'bnds'), fill_value=-9999.0)
        var_time_bnds.units = self._config.time_units
        var_time_bnds.calendar = self._config.calendar
        var_time_bnds[:] = -9999.0

        var_longitude = dataset.createVariable('lon', 'f4', ('lon',))
        var_longitude.units = 'degrees_east'

        var_latitude = dataset.createVariable('lat', 'f4', ('lat',))
        var_latitude.units = 'degrees_north'

        spatial_res = self._config.spatial_res
        lon0 = self._config.easting + image_x0 * spatial_res
        for i in range(image_width):
            var_longitude[i] = lon0 + i * spatial_res
        lat0 = self._config.northing + image_y0 * spatial_res
        for i in range(image_height):
            var_latitude[i] = lat0 - i * spatial_res

        # import time
        # dataset.source = 'CAB-LAB Software (module ' + __name__ + ')'
        # dataset.history = 'Created ' + time.ctime(time.time())
        #
        # check (nf 20151023) - add more global attributes from CF-conventions here,
        #                       especially those that reference original sources and originators
        #
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
        return self._datasets[var_index] if var_index >= 0 and var_index < len(self._datasets) else None

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
