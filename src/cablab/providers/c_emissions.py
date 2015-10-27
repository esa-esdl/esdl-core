from datetime import datetime
import os

import numpy

from cablab import BaseCubeSourceProvider
from cablab.util import NetCDFDatasetCache

VAR_NAME = 'C_Emissions'


class CEmissionsProvider(BaseCubeSourceProvider):
    def __init__(self, dir_path):
        super(CEmissionsProvider, self).__init__()
        self.dir_path = dir_path
        self.index_to_file = None
        self.dataset_cache = NetCDFDatasetCache(VAR_NAME)
        self.old_indices = None

    def prepare(self, cube_config):
        # todo - remove check once we have addressed spatial aggregation/interpolation
        if cube_config.grid_width != 1440 or cube_config.grid_height != 720:
            raise ValueError('illegal cube configuration, '
                             'provider does not yet implement spatial aggregation/interpolation')
        super(CEmissionsProvider, self).prepare(cube_config)

    def compute_images_from_sources(self, index_to_weight):

        # close all datasets that wont be used anymore
        new_indices = set(index_to_weight.keys())
        if self.old_indices:
            unused_indices = self.old_indices - new_indices
            for i in unused_indices:
                file, _ = self.index_to_file[i]
                self.dataset_cache.close_dataset(file)

        self.old_indices = new_indices

        if len(new_indices) == 1:
            i = next(iter(new_indices))
            file, time_index = self.index_to_file[i]
            dataset = self.dataset_cache.get_dataset(file)
            emissions = dataset.variables[VAR_NAME][time_index, :, :]
        else:
            emissions_sum = numpy.zeros((self.cube_config.grid_height, self.cube_config.grid_width),
                                        dtype=numpy.float32)
            weight_sum = 0.0
            for i in new_indices:
                weight = index_to_weight[i]
                file, time_index = self.index_to_file[i]
                dataset = self.dataset_cache.get_dataset(file)
                emissions = dataset.variables[VAR_NAME]
                emissions_sum += weight * emissions[time_index, :, :]
                weight_sum += weight
            emissions = emissions_sum / weight_sum

        return {VAR_NAME: emissions}

    def get_source_time_ranges(self):
        year_to_file = self._get_year_to_file_dict(self.dir_path)
        years = sorted(year_to_file.keys())
        source_time_ranges = []
        self.index_to_file = []
        for year in years:
            for month in range(1, 13):
                t1 = datetime(year, month, 1)
                if month < 12:
                    t2 = datetime(year, month + 1, 1)
                else:
                    t2 = datetime(year + 1, 1, 1)
                source_time_ranges.append((t1, t2))
                self.index_to_file.append((year_to_file[year], month - 1))
        return source_time_ranges

    def get_spatial_coverage(self):
        return 0, 0, 1440, 720

    def get_variable_metadata(self, variable):
        return {
            'datatype': numpy.float32,
            'fill_value': -9999.0,
            'units': 'g C m-2 month-1',
            'long_name': 'CASA-GFED4 BB',
            'scale_factor': 1.0,
            'add_offset': 0.0,
        }

    def close(self):
        self.dataset_cache.close_all_datasets()

    @staticmethod
    def _get_year_to_file_dict(dir_path):
        files = os.listdir(dir_path)
        file_dict = dict()
        for file in files:
            parts = file.split('.')
            if parts[-1] == 'gz' and parts[-2] == 'nc':
                year = int(parts[-3])
                file_dict[year] = os.path.join(dir_path, file)
        return file_dict
