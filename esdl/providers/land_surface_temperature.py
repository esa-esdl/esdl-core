import datetime
import os
from datetime import timedelta

import numpy

from esdl.cube_provider import NetCDFCubeSourceProvider


class LandSurfTemperatureProvider(NetCDFCubeSourceProvider):
    def __init__(self, cube_config, name='land_surface_temperature', dir=None, resampling_order=None):
        super(LandSurfTemperatureProvider, self).__init__(cube_config, name, dir, resampling_order)
        self.old_indices = None

    @property
    def variable_descriptors(self):
        return {
            'land_surface_temperature': {
                'source_name': 'LST',
                'data_type': numpy.float32,
                'fill_value': -32768.0,
                'units': 'K',
                'standard_name': 'surface_temperature',
                'long_name': 'Land Surface Temperature',
                'comment': 'Advanced Along Track Scanning Radiometer pixel land surface temperature product',
                'url': 'http://data.globtemperature.info/',
                'project_name' : 'GlobTemperature',
                'references' : 'Jiménez, C., et al. "Inversion of AMSR‐E observations for land surface temperature estimation: 1. Methodology and evaluation with station temperature." Journal of Geophysical Research: Atmospheres 122.6 (2017): 3330-3347.',
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

    def transform_source_image(self, source_image):
        """
        Transforms the source image, here by rotating and flipping.
        :param source_image: 2D image
        :return: source_image
        """
        return numpy.flipud(source_image)
