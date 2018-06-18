import datetime
import os
from datetime import timedelta

import numpy

from esdl.cube_provider import NetCDFCubeSourceProvider


class LaiFaparTipProvider(NetCDFCubeSourceProvider):
    def __init__(self, cube_config, name='lai_fapar_tip', dir=None, resampling_order=None):
        super(LaiFaparTipProvider, self).__init__(cube_config, name, dir, resampling_order)
        self.old_indices = None

    @property
    def variable_descriptors(self):
        # TODO: find out about references
        return {
            'leaf_area_index': {
                'source_name': 'Lai',
                'data_type': numpy.float32,
                'fill_value': numpy.nan,
                'units': '1',
                'standard_name': 'leaf_area_index',
                'long_name': 'Effective Leaf Area Index',
                'url': 'http://www.qa4ecv.eu/',
                'project_name': 'QA4ECV',
            },
            'fapar_tip': {
                'source_name': 'fapar',
                'data_type': numpy.float32,
                'fill_value': numpy.nan,
                'units': '1',
                'standard_name': 'fapar',
                'long_name': 'Fraction of Absorbed Photosynthetically Active Radiation',
                'url': 'http://www.qa4ecv.eu/',
                'project_name': 'QA4ECV',
            }
        }

    def compute_source_time_ranges(self):
        source_time_ranges = []
        file_names = os.listdir(self.dir_path)
        for file_name in file_names:
            if '.nc' in file_name:
                # print (file_name)
                source_date = datetime.datetime(int(file_name[22:26]), int(file_name[26:28]), int(file_name[28:30]), 12,
                                                00)
                if self.cube_config.start_time.year <= source_date.year <= self.cube_config.end_time.year:
                    file = os.path.join(self.dir_path, file_name).replace("\\", "/")
                    dataset = self.dataset_cache.get_dataset(file)
                    if self.variable_descriptors[self._name]["source_name"] in dataset.variables:
                        source_time_ranges.append(
                            (source_date - timedelta(hours=12), source_date + timedelta(hours=12), file, 0))
                    self.dataset_cache.close_dataset(file)
        return sorted(source_time_ranges, key=lambda item: item[0])

