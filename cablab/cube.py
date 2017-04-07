import math
import os
from datetime import datetime, timedelta

import netCDF4

import cablab
import cablab.util
from .cube_access import CubeDataAccess
from .cube_config import CubeConfig, CUBE_CHANGELOG
from .cube_provider import CubeSourceProvider
from .version import version as __version__


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
        # TODO (forman, 20151104): read from data cube's dir, see issue #5
        return ''

    @property
    def closed(self):
        """
        Checks if the cube has been closed.
        """
        return self._closed

    @property
    def data(self) -> CubeDataAccess:
        """
        The cube's data which is an instance of the **CubeDataAccess** class.
        """
        if not self._data:
            self._data = CubeDataAccess(self.config, self.base_dir)
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
        with open(os.path.join(base_dir, 'CHANGELOG'), 'w') as fp:
            fp.write(CUBE_CHANGELOG)
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
            # Close all open datasets of last year (which have been processed)
            for key in datasets:
                if target_year - 1 == int(key[0:4]):
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
        time_bnds = dataset.variables['time_bnds']
        if time_bnds[time_index, 1] != t2:
            print("Warning: Time stamps discrepancy: %f is is not %f" % (time_bnds[time_index, 1], t2))
            print("target start: %s, target end %s" % (target_start_time, target_end_time))

        var_variable = dataset.variables[var_name]
        var_variable[time_index, :, :] = image

    def _init_variable_dataset(self, provider, dataset, variable_name, start_year):
        import time

        # TODO (forman, 20160512): some of these attributes could be read from cube configuration
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

        num_periods_per_year = self._config.num_periods_per_year
        dataset.createDimension('bnds', 2)
        dataset.createDimension('time', num_periods_per_year)
        dataset.createDimension('lat', image_height)
        dataset.createDimension('lon', image_width)

        temporal_res = self._config.temporal_res
        start_date = datetime(start_year, 1, 1, 0, 0)
        start_num = self._config.date2num(start_date)
        var_time_bnds = dataset.createVariable('time_bnds', 'f8', ('time', 'bnds'), fill_value=-9999.0)
        var_time_bnds.units = self._config.time_units
        var_time_bnds.calendar = self._config.calendar
        lower_bounds = [start_num + temporal_res * (i + 0.0) for i in range(num_periods_per_year)]
        upper_bounds = [start_num + temporal_res * (i + 1.0) for i in range(num_periods_per_year)]
        upper_bounds[-1] = self._config.date2num(datetime(start_year + 1, 1, 1, 0, 0))
        var_time_bnds[:, 0] = lower_bounds
        var_time_bnds[:, 1] = upper_bounds

        var_time = dataset.createVariable('time', 'f8', ('time',), fill_value=-9999.0)
        var_time.long_name = 'time'
        var_time.standard_name = 'time'
        var_time.units = self._config.time_units
        var_time.calendar = self._config.calendar
        var_time.bounds = 'time_bnds'

        times = [start_num + temporal_res * (i + 0.5) for i in range(num_periods_per_year)]
        # times[-1] = var_time_bnds[-1,0] + (var_time_bnds[-1,1] - var_time_bnds[-1,0]) / 2.
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
            var_longitude_bnds[i, 0] = lon
            var_longitude_bnds[i, 1] = lon + spatial_res

        lat0 = self._config.northing + image_y0 * spatial_res
        for i in range(image_height):
            lat = lat0 - i * spatial_res
            var_latitude[i] = lat - 0.5 * spatial_res
            var_latitude_bnds[i, 0] = lat - spatial_res
            var_latitude_bnds[i, 1] = lat

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
                    # TODO (forman, 20160512): log, or print to stderr
                    print('%s = %s failed (%s)!' % (name, value, str(ve)))
        return dataset

    @staticmethod
    def _get_num_steps(x1, x2, dx):
        return int(math.floor((x2 - x1) / dx))
