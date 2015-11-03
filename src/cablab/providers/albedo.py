import os

import numpy

from cablab import BaseCubeSourceProvider
from cablab.util import NetCDFDatasetCache, day2date
from skimage.transform import resize

VAR_NAME = 'Snow_Fraction'


class AlbedoProvider(BaseCubeSourceProvider):
    def __init__(self, cube_config, dir_path):
        super(AlbedoProvider, self).__init__(cube_config)
        # todo (hp 20151030) - remove check once we have addressed spatial aggregation/interpolation
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
                'units': '1',
                'long_name': 'Snow Fraction',
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
                file, _ = self._get_file_and_time_index(i)
                self.dataset_cache.close_dataset(file)

        self.old_indices = new_indices

        if len(new_indices) == 1:
            i = next(iter(new_indices))
            file, _ = self._get_file_and_time_index(i)
            dataset = self.dataset_cache.get_dataset(file)
            snow_fraction = dataset.variables[VAR_NAME][:, :]
            snow_fraction = resize(snow_fraction, (720, 1440), preserve_range=True, order=3)
        else:
            snow_fraction_sum = numpy.zeros((self.cube_config.grid_height, self.cube_config.grid_width),
                                            dtype=numpy.float32)
            weight_sum = 0.0
            for i in new_indices:
                weight = index_to_weight[i]
                file, time_index = self._get_file_and_time_index(i)
                dataset = self.dataset_cache.get_dataset(file)
                snow_fraction = dataset.variables[VAR_NAME][:, :]
                snow_fraction = resize(snow_fraction, (720, 1440), preserve_range=True, order=3)
                snow_fraction_sum += weight * snow_fraction[:, :]
                weight_sum += weight
            snow_fraction = snow_fraction_sum / weight_sum

        return {VAR_NAME: snow_fraction}

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

        for root, sub_dirs, files in os.walk(self.dir_path):
            for sub_dir in sub_dirs:
                sub_dir_path = os.path.join(self.dir_path, sub_dir)
                file_names = os.listdir(sub_dir_path)
                for file_name in file_names:
                    if file_name.endswith('.nc.gz'):
                        file = os.path.join(sub_dir_path, file_name)
                        self.dataset_cache.get_dataset(file)
                        time_info = file_name.split('.', 2)[1]
                        t1, t2 = day2date(int(time_info))
                        self.dataset_cache.close_dataset(file)
                        source_time_ranges.append((t1, t2, file, 0))
        self.source_time_ranges = sorted(source_time_ranges, key=lambda item: item[0])
