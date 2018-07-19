import os
from datetime import timedelta

import netCDF4
import numpy as np

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
                'data_type': np.float32,
                'fill_value': np.nan,
                'units': '1',
                'standard_name': 'leaf_area_index',
                'long_name': 'Effective Leaf Area Index',
                'url': 'http://www.qa4ecv.eu/',
                'project_name': 'QA4ECV',
            },
            'fapar_tip': {
                'source_name': 'fapar',
                'data_type': np.float32,
                'fill_value': np.nan,
                'units': '1',
                'standard_name': 'fapar',
                'long_name': 'Fraction of Absorbed Photosynthetically Active Radiation',
                'url': 'http://www.qa4ecv.eu/',
                'project_name': 'QA4ECV',
            }
        }

    def compute_source_time_ranges(self):
        source_time_ranges = []
        for root, sub_dirs, files in os.walk(self.dir_path):
            for sub_dir in sub_dirs:
                source_year = int(sub_dir)
                if self.cube_config.start_time.year <= source_year <= self.cube_config.end_time.year:
                    sub_dir_path = os.path.join(self.dir_path, sub_dir, "005")
                    file_names = os.listdir(sub_dir_path)
                    for file_name in file_names:
                        if '.nc' in file_name:
                            file = os.path.join(sub_dir_path, file_name)
                            dataset = self.dataset_cache.get_dataset(file)
                            time = netCDF4.num2date(dataset.variables['time'][0],
                                                    dataset.variables['time'].units,
                                                    calendar=dataset.variables['time'].calendar)
                            self.dataset_cache.close_dataset(file)
                            source_time_ranges.append((time, time + timedelta(days=1), file, 0))
        return sorted(source_time_ranges, key=lambda item: item[0])
