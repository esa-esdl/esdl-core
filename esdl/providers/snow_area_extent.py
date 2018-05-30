import os
from datetime import timedelta

import netCDF4
import numpy

from esdl.cube_provider import NetCDFCubeSourceProvider

VAR_NAME = 'MFSC'
FILL_VALUE = -9999


class SnowAreaExtentProvider(NetCDFCubeSourceProvider):
    def __init__(self, cube_config, name='snow_area_extent', dir=None, resampling_order=None):
        super(SnowAreaExtentProvider, self).__init__(cube_config, name, dir, resampling_order)
        self.old_indices = None

    @property
    def variable_descriptors(self):
        return {
            'fractional_snow_cover': {
                'source_name': 'MFSC',
                'data_type': numpy.float32,
                'fill_value': -9999.0,
                'units': 'percent',
                'standard_name': 'surface_snow_area_fraction',
                'long_name': 'Surface fraction covered by snow.',
                'references': 'Luojus, Kari, et al. "ESA DUE Globsnow-Global Snow Database for Climate Research." '
                              'ESA Special Publication. Vol. 686. 2010.',
                'comment': 'Grid cell fractional snow cover based on the Globsnow CCI product.',
                'url': 'http://www.globsnow.info/',
                'project_name' : 'GlobSnow',
            }
        }

    def compute_source_time_ranges(self):
        source_time_ranges = []
        file_names = os.listdir(self.dir_path)
        for file_name in file_names:
            file = os.path.join(self.dir_path, file_name)
            dataset = self.dataset_cache.get_dataset(file)
            time = dataset.variables['time']
            # dates = netCDF4.num2date(time[:], time.units, calendar=time.calendar)
            dates = netCDF4.num2date(time[:] - 14, 'days since 1582-10-15 00:00', calendar='gregorian')
            self.dataset_cache.close_dataset(file)
            n = len(dates)
            for i in range(n):
                t1 = dates[i]
                if i < n - 1:
                    t2 = dates[i + 1]
                else:
                    t2 = t1 + timedelta(days=31)  # assuming it's December
                source_time_ranges.append((t1, t2, file, i))
        return sorted(source_time_ranges, key=lambda item: item[0])
