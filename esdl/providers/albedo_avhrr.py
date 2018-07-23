import os
from datetime import timedelta

import numpy as np
from netCDF4 import num2date

from esdl.cube_provider import NetCDFCubeSourceProvider


class AlbedoAVHRRProvider(NetCDFCubeSourceProvider):
    def __init__(self, cube_config, name='albedo', dir=None, resampling_order=None):
        super(AlbedoAVHRRProvider, self).__init__(cube_config, name, dir, resampling_order)
        self.old_indices = None

    @property
    def variable_descriptors(self):
        # TODO: find out about the references
        return {
            'white_sky_albedo_avhrr': {
                'source_name': 'BHR_VIS',
                'data_type': np.float32,
                'fill_value': -9999.0,
                'units': '1',
                'long_name': 'Bi-Hemisphere Reflectance albedo - VIS band',
                'standard_name': 'surface_albedo_white_sky',
                'comment': 'White sky albedo derived from the QA4ECV Albedo Product',
                'url': 'http://www.qa4ecv.eu/',
                'project_name': 'QA4ECV - European Union Framework Program 7',
            },
            'black_sky_albedo_avhrr': {
                'source_name': 'DHR_VIS',
                'data_type': np.float32,
                'fill_value': -9999.0,
                'units': '1',
                'standard_name': 'surface_albedo_black_sky',
                'long_name': 'Directional Hemisphere Reflectance albedo - VIS band',
                'comment': 'Black sky albedo derived from the QA4ECV Albedo Product',
                'url': 'http://www.qa4ecv.eu/',
                'project_name': 'QA4ECV - European Union Framework Program 7',
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
                            time = num2date(dataset.variables['time'][0],
                                            dataset.variables['time'].units,
                                            calendar='gregorian')
                            self.dataset_cache.close_dataset(file)
                            source_time_ranges.append((time, time + timedelta(days=1), file, 0))
        return sorted(source_time_ranges, key=lambda item: item[0])

    def transform_source_image(self, source_image):
        """
        Transforms the source image, here by flipping and then shifting horizontally.
        :param source_image: 2D image
        :return: source_image
        """
        source_image[(source_image < 0) | (source_image > 1)] = np.nan
        return source_image
