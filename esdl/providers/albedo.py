import datetime
import os

import numpy
from netCDF4 import date2num, num2date

from esdl.cube_provider import NetCDFCubeSourceProvider


class AlbedoProvider(NetCDFCubeSourceProvider):
    def __init__(self, cube_config, name='albedo', dir=None, resampling_order=None):
        super(AlbedoProvider, self).__init__(cube_config, name, dir, resampling_order)
        self.old_indices = None

    @property
    def variable_descriptors(self):
        return {
            'white_sky_albedo': {
                'source_name': 'BHR_VIS',
                'data_type': numpy.float32,
                'fill_value': numpy.nan,
                'units': '-',
                'long_name': 'White Sky Albedo for Visible Wavebands',
                'standard_name': 'surface_albedo_white_sky',
                'references': 'Muller, Jan-Peter, et al. "The ESA GLOBALBEDO project for mapping the Earth’s '
                              'land surface albedo for 15 years from European sensors." Geophysical Research '
                              'Abstracts. Vol. 13. 2012.',
                'comment': 'White sky albedo derived from the GlobAlbedo CCI project dataset',
                'url': 'http://www.globalbedo.org/',
                'project_name' : 'GlobAlbedo',
            },
            'black_sky_albedo': {
                'source_name': 'DHR_VIS',
                'data_type': numpy.float32,
                'fill_value': numpy.nan,
                'units': '-',
                'standard_name': 'surface_albedo_black_sky',
                'long_name': 'Black Sky Albedo for Visible Wavebands',
                'references': 'Muller, Jan-Peter, et al. "The ESA GLOBALBEDO project for mapping the Earth’s '
                              'land surface albedo for 15 years from European sensors." Geophysical Research '
                              'Abstracts. Vol. 13. 2012.',
                'comment': 'Black sky albedo derived from the GlobAlbedo CCI project dataset',
                'url': 'http://www.globalbedo.org/',
                'project_name' : 'GlobAlbedo',
            }
        }

    def compute_source_time_ranges(self):
        source_time_ranges = []

        file_names = os.listdir(self.dir_path)
        for file_name in file_names:
            time_info = file_name.split('.', 5)[4]
            t1, t2 = self.day2date(int(time_info))
            if self.cube_config.start_time <= t1 <= self.cube_config.end_time:
                file = os.path.join(self.dir_path, file_name)
                self.dataset_cache.get_dataset(file)
                self.dataset_cache.close_dataset(file)
                source_time_ranges.append((t1, t2, file, 0))

        return sorted(source_time_ranges, key=lambda item: item[0])

    @staticmethod
    def day2date(times):
        """
        Return datetime objects given numeric time values in year and day format.
        For example, 2005021 corresponds to the 21st day of year 2005.

        >>> AlbedoProvider.day2date(2000001)
        (datetime.datetime(2000, 1, 1, 0, 0), datetime.datetime(2000, 1, 9, 0, 0))
        >>> AlbedoProvider.day2date(2000361)
        (datetime.datetime(2000, 12, 26, 0, 0), datetime.datetime(2001, 1, 3, 0, 0))

        :param times: numeric time values
        :return: datetime.datetime values
        """
        year = times // 1000
        year_start_date = date2num(datetime.datetime(year, 1, 1), units='days since 0001-1-1 00:00',
                                   calendar='gregorian')

        day = times % 1000 - 1
        actual_start_date = year_start_date + day
        actual_end_date = actual_start_date + 8

        return num2date(actual_start_date, units='days since 0001-1-1 00:00', calendar='gregorian'), num2date(
            actual_end_date, units='days since 0001-1-1 00:00',
            calendar='gregorian')
