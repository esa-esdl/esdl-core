import os
from datetime import timedelta

import netCDF4
import numpy

from esdl.cube_provider import NetCDFCubeSourceProvider


class PrecipProvider(NetCDFCubeSourceProvider):
    def __init__(self, cube_config, name='precip', dir=None, resampling_order=None):
        super(PrecipProvider, self).__init__(cube_config, name, dir, resampling_order)
        self.old_indices = None

    @property
    def variable_descriptors(self):
        return {
            'precipitation': {
                'source_name': 'Precip',
                'data_type': numpy.float32,
                'fill_value': -9999.0,
                'units': 'mm/day',
                'long_name': 'Precip - RealTime [RT] (see documentation for more information)',
                'standard_name': 'precipitation_flux',
                'references': 'Adler, Robert F., et al. "The version-2 global precipitation climatology project (GPCP) '
                              'monthly precipitation analysis (1979-present)." Journal of hydrometeorology 4.6 '
                              '(2003): 1147-1167.',
                'comment': 'Precipitation based on the GPCP dataset.',
                'url': 'http://precip.gsfc.nasa.gov/',
                'project_name': 'GPCP',
            }
        }

    def compute_source_time_ranges(self):
        source_time_ranges = []
        file_names = os.listdir(self.dir_path)
        for file_name in file_names:
            file = os.path.join(self.dir_path, file_name)
            dataset = self.dataset_cache.get_dataset(file)
            time = dataset.variables['time']
            dates = netCDF4.num2date(time[:], calendar=time.calendar, units=time.units)
            self.dataset_cache.close_dataset(file)
            source_time_ranges += [(dates[i], dates[i] + timedelta(days=1), file, i) for i in range(len(dates))]
        return sorted(source_time_ranges, key=lambda item: item[0])
