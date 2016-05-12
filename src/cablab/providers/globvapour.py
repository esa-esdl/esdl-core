import os
from datetime import datetime, timedelta

import gridtools.resampling as gtr
import netCDF4
import numpy

from cablab import NetCDFCubeSourceProvider
from cablab.util import aggregate_images

VAR_NAME = 'tcwv_res'
FILL_VALUE = -999.0


class GlobVapourProvider(NetCDFCubeSourceProvider):
    def __init__(self, cube_config, name, dir_path):
        super(GlobVapourProvider, self).__init__(cube_config, name, dir_path)
        self.old_indices = None

    @property
    def variable_descriptors(self):
        return {
            VAR_NAME: {
                'data_type': numpy.float32,
                'fill_value': FILL_VALUE,
                'units': 'kg m-2',
                'long_name': 'Total Column Water Vapour',
                'scale_factor': 1.0,
                'add_offset': 0.0,
            }
        }

    # todo: test, then remove method and test again using base class version of method
    # Special in this implementation:
    #   - VAR_NAME name is 'Ozone', but in NetCDF files there is 'atmosphere_mole_content_of_ozone'
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
            var_image = self.dataset_cache.get_dataset(file).variables[VAR_NAME][time_index, :, :]
        else:
            images = [None] * len(new_indices)
            weights = [None] * len(new_indices)
            j = 0
            for i in new_indices:
                file, time_index = self._get_file_and_time_index(i)
                images[j] = self.dataset_cache.get_dataset(file).variables[VAR_NAME][time_index, :, :]
                weights[j] = index_to_weight[i]
                j += 1
            var_image = aggregate_images(images, weights=weights)

        var_image = gtr.resample_2d(var_image, self.cube_config.grid_width, self.cube_config.grid_height,
                                    us_method=gtr.US_NEAREST, fill_value=FILL_VALUE)
        return {VAR_NAME: var_image}

    def compute_source_time_ranges(self):
        source_time_ranges = []
        dir_names = os.listdir(self.dir_path)

        for dir_name in dir_names:
            file_names = os.listdir(os.path.join(self.dir_path, dir_name))
            for file_name in file_names:
                file = os.path.join(self.dir_path, dir_name, file_name)
                dataset = self.dataset_cache.get_dataset(file)
                time = dataset.variables['time']
                dates1 = netCDF4.num2date(time[:], 'days since 1970-01-01 00:00:00', calendar='gregorian')
                self.dataset_cache.close_dataset(file)
                t1 = datetime(dates1.year, dates1.month, dates1.day)
                # use this one for weekly data
                # t2 = t1 +  timedelta(days=7)
                t2 = self._last_day_of_month(t1) + timedelta(days=1)
                source_time_ranges.append((t1, t2, file, 0))
        return sorted(source_time_ranges, key=lambda item: item[0])

    @staticmethod
    def _last_day_of_month(any_day):
        next_month = any_day.replace(day=28) + timedelta(days=4)
        return next_month - timedelta(days=next_month.day)
