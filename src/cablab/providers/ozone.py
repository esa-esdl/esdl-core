import os
from  datetime import datetime

import numpy
import netCDF4
import gridtools.resampling as gtr

from cablab import BaseCubeSourceProvider
from cablab.util import NetCDFDatasetCache, aggregate_images

VAR_NAME = 'Ozone'
FILL_VALUE = numpy.NaN


class OzoneProvider(BaseCubeSourceProvider):
    def __init__(self, cube_config, dir_path):
        super(OzoneProvider, self).__init__(cube_config)
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
                'units': 'DU',
                'long_name': 'Mean Total Ozone Column in Dobson Units',
                'standard_name': 'atmosphere_mole_content_of_ozone',
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
                file = self._get_file(i)
                self.dataset_cache.close_dataset(file)

        self.old_indices = new_indices

        if len(new_indices) == 1:
            i = next(iter(new_indices))
            file = self._get_file(i)
            ozone = self.dataset_cache.get_dataset(file).variables['atmosphere_mole_content_of_ozone'][:, :]
        else:
            images = [None] * len(new_indices)
            weights = [None] * len(new_indices)
            j = 0
            for i in new_indices:
                file = self._get_file(i)
                images[j] = self.dataset_cache.get_dataset(file).variables['atmosphere_mole_content_of_ozone'][:, :]
                weights[j] = index_to_weight[i]
                j += 1
            ozone = aggregate_images(images, weights=weights)

        ozone = gtr.resample2d(ozone, self.cube_config.grid_width, self.cube_config.grid_height,
                               us_method=gtr.US_NEAREST, fill_value=FILL_VALUE)
        return {VAR_NAME: ozone}

    def _get_file(self, i):
        return self.source_time_ranges[i][2]

    def get_source_time_ranges(self):
        return self.source_time_ranges

    def get_spatial_coverage(self):
        return 0, 0, self.cube_config.grid_width, self.cube_config.grid_height

    def close(self):
        self.dataset_cache.close_all_datasets()

    def _init_source_time_ranges(self):
        file_names = os.listdir(self.dir_path)
        source_time_ranges = list()
        for file_name in file_names:
            file = os.path.join(self.dir_path, file_name)
            dataset = netCDF4.Dataset(file)
            t1 = dataset.time_coverage_start
            t2 = dataset.time_coverage_end
            dataset.close()
            source_time_ranges.append((datetime(int(t1[0:4]), int(t1[4:6]), int(t1[6:8])),
                                       datetime(int(t2[0:4]), int(t2[4:6]), int(t2[6:8])),
                                       file))
        self.source_time_ranges = sorted(source_time_ranges, key=lambda item: item[0])
