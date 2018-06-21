import os
from datetime import datetime, timedelta

import netCDF4
import numpy

from esdl.cube_provider import NetCDFCubeSourceProvider


class GlobVapourProvider(NetCDFCubeSourceProvider):
    def __init__(self, cube_config, name='globvapour', dir=None, resampling_order=None):
        super(GlobVapourProvider, self).__init__(cube_config, name, dir, resampling_order)
        self.old_indices = None

    @property
    def variable_descriptors(self):
        return {
            'water_vapour': {
                'source_name': 'tcwv_res',
                'data_type': numpy.float32,
                'fill_value': -999.0,
                'units': 'kg m-2',
                'long_name': 'Total Column Water Vapour',
                'standard_name': 'atmosphere_mass_content_of_water_vapor',
                'references': 'Schneider, Nadine, et al. "ESA DUE GlobVapour water vapor products: Validation." '
                              'AIP Conference Proceedings. Vol. 1531. No. 1. 2013.',
                'comment': 'Total column water vapour based on the GlobVapour CCI product.',
                'url': 'http://www.globvapour.info/',
                'project_name' : 'GlobVapour',
            }
        }

    def compute_source_time_ranges(self):
        source_time_ranges = []
        dir_names = os.listdir(self.dir_path)

        for dir_name in dir_names:
            file_names = os.listdir(os.path.join(self.dir_path, dir_name))
            for file_name in file_names:
                file = os.path.join(self.dir_path, dir_name, file_name)
                dataset = self.dataset_cache.get_dataset(file)
                time = dataset.variables['time']
                dates1 = netCDF4.num2date(time[:], 'days since 1970-01-01 00:00:00', calendar='gregorian')
                self.dataset_cache.close_dataset(file)
                t1 = datetime(dates1.year, dates1.month, dates1.day)
                # use this one for weekly data
                # t2 = t1 +  timedelta(days=7)
                t2 = self._last_day_of_month(t1) + timedelta(days=1)
                source_time_ranges.append((t1, t2, file, 0))
        return sorted(source_time_ranges, key=lambda item: item[0])

    @staticmethod
    def _last_day_of_month(any_day):
        next_month = any_day.replace(day=28) + timedelta(days=4)
        return next_month - timedelta(days=next_month.day)
