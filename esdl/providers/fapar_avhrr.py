import os
from datetime import datetime

import numpy as np

from esdl.cube_provider import NetCDFCubeSourceProvider


class FaparAvhrrProvider(NetCDFCubeSourceProvider):
    def __init__(self, cube_config, name='fapar_avhrr', dir=None, resampling_order=None):
        super(FaparAvhrrProvider, self).__init__(cube_config, name, dir, resampling_order)
        self.old_indices = None

    @property
    def variable_descriptors(self):
        # TODO: find out about references
        # TODO: find out how to enter byte as valid min and valid max.
        return {
            'fapar_avhrr': {
                'source_name': 'FAPAR',
                'data_type': np.byte,
                'fill_value': -1,
                'valid_min': 0,
                'valid_max': -2,
                'real_valid_min': 0.0,
                'real_valid_max': 1.0,
                'units': '-',
                'scale_factor': 0.003937008,
                'standard_name': 'fraction_of_surface_downwelling_photosynthetic_radiative_flux_absorbed_by_vegetation',
                'long_name': 'Weighted Mean (FAPAR)',
                'url': 'http://www.qa4ecv.eu/',
                'project_name': 'QA4ECV',
            }
        }

    def compute_source_time_ranges(self):
        source_time_ranges = []
        file_names = os.listdir(self.dir_path)
        for file_name in file_names:
            time_info1 = file_name.split('_', 4)[2]
            time_info2 = file_name.split('_', 4)[3]
            date1 = FaparAvhrrProvider.int2date(int(time_info1))
            date2 = FaparAvhrrProvider.int2date(int(time_info2))
            if self.cube_config.start_time <= date1 <= self.cube_config.end_time:
                if '.NC.gz' in file_name:
                    file = os.path.join(self.dir_path, file_name)
                    self.dataset_cache.close_dataset(file)
                    source_time_ranges.append((date1, date2, file, 0))
        return sorted(source_time_ranges, key=lambda item: item[0])

    def transform_source_image(self, source_image):
        """
        Transforms the source image, here by flipping and then shifting horizontally.
        :param source_image: 2D image
        :return: source_image
        """
        return np.flipud(source_image)

    @staticmethod
    def int2date(time_int: int):
        """
        Return datetime objects given numeric time values in year and day format.
        For example, 2005021 corresponds to the 21st day of year 2005.

        >>> FaparAvhrrProvider.int2date(19820101)
        datetime.datetime(1982, 1, 1, 0, 0)
        >>> FaparAvhrrProvider.int2date(19830211)
        datetime.datetime(1983, 02, 11, 0, 0)

        :param time_int: time in integer with the format yyyymmdd
        :return: datetime.datetime values the time in datetime format
        """
        year = time_int // 10000
        month = (time_int // 100) % 100
        day = time_int % 100

        return datetime(year=year, month=month, day=day)
