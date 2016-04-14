from datetime import timedelta
import os

import numpy
import netCDF4

from cablab import BaseCubeSourceProvider
from cablab.util import NetCDFDatasetCache
from skimage.measure import block_reduce
import cablab.resize as resize

VAR_NAME = 'MFSC'


class SnowAreaExtentProvider(BaseCubeSourceProvider):
    def __init__(self, cube_config, dir_path):
        super(SnowAreaExtentProvider, self).__init__(cube_config)
        # todo (hp 20151030) - remove check once we have addressed spatial aggregation/interpolation, see issue #3
        if cube_config.grid_width != 1440 or cube_config.grid_height != 720:
            raise ValueError('illegal cube configuration, '
                             'provider does not yet implement spatial aggregation/interpolation')
        self.dir_path = dir_path
        self.dataset_cache = NetCDFDatasetCache(VAR_NAME)
        self.source_time_ranges = None
        self.old_indices = None

    def prepare(self):
        self._init_source_time_ranges()

    def get_variable_descriptors(self):
        return {
            VAR_NAME: {
                'data_type': numpy.float32,
                'fill_value': -9999.0,
                'units': 'percent',
                'long_name': 'Level 3B Fractional Snow Cover (%)  Aggregated Monthly',
            }
        }

    def compute_variable_images_from_sources(self, index_to_weight):

        # close all datasets that wont be used anymore
        new_indices = set(index_to_weight.keys())
        if self.old_indices:
            unused_indices = self.old_indices - new_indices
            for i in unused_indices:
                file, _ = self._get_file_and_time_index(i)
                self.dataset_cache.close_dataset(file)

        self.old_indices = new_indices

        if len(new_indices) == 1:
            i = next(iter(new_indices))
            file, time_index = self._get_file_and_time_index(i)
            dataset = self.dataset_cache.get_dataset(file)
            snow_area_extent = 1.0 * dataset.variables[VAR_NAME][time_index, :, :]
            snow_area_extent.filled(numpy.nan)
        else:
            weight_sum = 0.0
            snow_area_extent_sum = numpy.zeros((18000, 36000), dtype=numpy.float64)
            for i in new_indices:
                weight = index_to_weight[i]
                file, time_index = self._get_file_and_time_index(i)
                dataset = self.dataset_cache.get_dataset(file)
                snow_area_extent = dataset.variables[VAR_NAME]
                snow_area_extent_sum += weight * snow_area_extent[time_index, :, :]
                weight_sum += weight
            snow_area_extent = snow_area_extent_sum / weight_sum

        lat_size, lon_size = snow_area_extent.shape

        latitude_downscale_factor = lat_size / self.cube_config.grid_height
        longitude_downscale_factor = lon_size / self.cube_config.grid_width

        if latitude_downscale_factor != longitude_downscale_factor or latitude_downscale_factor % 1 > 0:
            raise ValueError('illegal downscale factor, '
                             'the downscale factor has to be an integer value.')

        snow_area_extent = resize.resize(lon_size, lat_size, snow_area_extent, self.cube_config.grid_width,
                                         self.cube_config.grid_height)

        return {VAR_NAME: snow_area_extent}

    def _get_file_and_time_index(self, i):
        return self.source_time_ranges[i][2:4]

    def get_source_time_ranges(self):
        return self.source_time_ranges

    def get_spatial_coverage(self):
        return 0, 0, 1440, 720

    def close(self):
        self.dataset_cache.close_all_datasets()

    def _init_source_time_ranges(self):
        source_time_ranges = []
        file_names = os.listdir(self.dir_path)
        for file_name in file_names:
            file = os.path.join(self.dir_path, file_name)
            dataset = self.dataset_cache.get_dataset(file)
            time = dataset.variables['time']
            # dates = netCDF4.num2date(time[:], time.units, calendar=time.calendar)
            dates = netCDF4.num2date(time[:] - 14, 'days since 1582-10-15 00:00', calendar='gregorian')
            self.dataset_cache.close_dataset(file)
            n = len(dates)
            for i in range(n):
                t1 = dates[i]
                if i < n - 1:
                    t2 = dates[i + 1]
                else:
                    t2 = t1 + timedelta(days=31)  # assuming it's December
                source_time_ranges.append((t1, t2, file, i))
        self.source_time_ranges = sorted(source_time_ranges, key=lambda item: item[0])
