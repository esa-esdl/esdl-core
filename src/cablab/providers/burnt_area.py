from datetime import datetime
import os

import numpy
import netCDF4
import gridtools.resampling as gtr

from cablab import BaseCubeSourceProvider
from cablab.util import NetCDFDatasetCache, aggregate_images

VAR_NAME = 'BurntArea'
FILL_VALUE = -9999.0


class BurntAreaProvider(BaseCubeSourceProvider):
    def __init__(self, cube_config, dir_path):
        super(BurntAreaProvider, self).__init__(cube_config)
        self.dir_path = dir_path
        self.source_time_ranges = None
        self.dataset_cache = NetCDFDatasetCache(VAR_NAME)
        self.old_indices = None

    def prepare(self):
        self._init_source_time_ranges()

    def get_variable_descriptors(self):
        return {
            VAR_NAME: {
                'data_type': numpy.float32,
                'fill_value': FILL_VALUE,
                'units': 'hectares',
                'long_name': 'Monthly Burnt Area',
                'scale_factor': 1.0,
                'add_offset': 0.0,
            }
        }

    def compute_variable_images_from_sources(self, index_to_weight):

        # close all datasets that wont be used anymore
        new_indices = set(index_to_weight.keys())
        if self.old_indices:
            unused_indices = self.old_indices - new_indices
            for i in unused_indices:
                file, time_index = self._get_file_and_time_index(i)
                self.dataset_cache.close_dataset(file)

        self.old_indices = new_indices

        if len(new_indices) == 1:
            i = next(iter(new_indices))
            file, time_index = self._get_file_and_time_index(i)
            burnt_area = self.dataset_cache.get_dataset(file).variables[VAR_NAME][time_index, :, :]
        else:
            images = [None] * len(new_indices)
            weights = [None] * len(new_indices)
            j = 0
            for i in new_indices:
                file, time_index = self._get_file_and_time_index(i)
                images[j] = self.dataset_cache.get_dataset(file).variables[VAR_NAME][time_index, :, :]
                weights[j] = index_to_weight[i]
                j += 1
            burnt_area = aggregate_images(images, weights=weights)

        burnt_area = gtr.resample2d(burnt_area, self.cube_config.grid_width, self.cube_config.grid_height,
                                    us_method=gtr.US_NEAREST, fill_value=FILL_VALUE)
        return {VAR_NAME: burnt_area}

    def _get_file_and_time_index(self, i):
        return self.source_time_ranges[i][2:4]

    def get_source_time_ranges(self):
        return self.source_time_ranges

    def get_spatial_coverage(self):
        return 0, 0, self.cube_config.grid_width, self.cube_config.grid_height

    def close(self):
        self.dataset_cache.close_all_datasets()

    def _init_source_time_ranges(self):
        source_time_ranges = []
        file_names = os.listdir(self.dir_path)
        for file_name in file_names:
            file = os.path.join(self.dir_path, file_name)
            dataset = self.dataset_cache.get_dataset(file)
            time_bnds = dataset.variables['time_bnds']
            # todo (nf 20151028) - check datetime units, may be wrong in either the netCDF file (which is
            # 'days since 1582-10-14 00:00') or the netCDF4 library
            dates1 = netCDF4.num2date(time_bnds[:, 0], 'days since 1582-10-24 00:00', calendar='gregorian')
            dates2 = netCDF4.num2date(time_bnds[:, 1], 'days since 1582-10-24 00:00', calendar='gregorian')
            self.dataset_cache.close_dataset(file)
            for i in range(len(dates1)):
                t1 = datetime(dates1[i].year, dates1[i].month, dates1[i].day)
                t2 = datetime(dates2[i].year, dates2[i].month, dates2[i].day)
                source_time_ranges.append((t1, t2, file, i))
        self.source_time_ranges = sorted(source_time_ranges, key=lambda item: item[0])
