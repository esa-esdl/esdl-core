import os
from datetime import timedelta

import gridtools.resampling as gtr
import netCDF4
import numpy

from cablab import NetCDFCubeSourceProvider

VAR_NAME = 'MFSC'
FILL_VALUE = -9999


class SnowAreaExtentProvider(NetCDFCubeSourceProvider):
    def __init__(self, cube_config, name='snow_area_extent', dir=None):
        super(SnowAreaExtentProvider, self).__init__(cube_config, name, dir)
        self.old_indices = None

    @property
    def variable_descriptors(self):
        return {
            'fractional_snow_cover': {
                'source_name': 'MFSC',
                'data_type': numpy.float32,
                'fill_value': -9999.0,
                'units': 'percent',
                'standard_name': 'surface_snow_area_fraction'
                'long_name': 'Surface fraction covered by snow.',
                'references': 'Luojus, Kari, et al. "ESA DUE Globsnow-Global Snow Database for Climate Research." ESA Special Publication. Vol. 686. 2010.',
                'comment': 'Grid cell fractional snow cover based on the Globsnow CCI product.',
                'url': 'http://www.globsnow.info/',
            }
        }

    # todo: test, then remove method and test again using base class version of method
    # Special in this implementation:
    #  - aggregate_image not called, see Hans' memory problem,
    #  - performs it's own temporal aggregation which is wrong because it doesn't consider masked values
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
            var_image = 1.0 * self.dataset_cache.get_dataset(file).variables[VAR_NAME][time_index, :, :]
        else:
            weight_sum = 0.0
            snow_area_extent_sum = numpy.zeros((18000, 36000), dtype=numpy.float64)
            for i in new_indices:
                weight = index_to_weight[i]
                file, time_index = self._get_file_and_time_index(i)
                var_image = self.dataset_cache.get_dataset(file).variables[VAR_NAME]
                snow_area_extent_sum += weight * var_image[time_index, :, :]
                weight_sum += weight
            # todo: produces memory error when using aggregate_image function
            var_image = snow_area_extent_sum / weight_sum

        var_image = gtr.resample_2d(var_image, self.cube_config.grid_width, self.cube_config.grid_height,
                                    us_method=gtr.US_NEAREST, fill_value=FILL_VALUE)
        return {VAR_NAME: var_image}

    def compute_source_time_ranges(self):
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
        return sorted(source_time_ranges, key=lambda item: item[0])
