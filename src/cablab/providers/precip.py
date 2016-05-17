import os
from datetime import timedelta

import netCDF4
import numpy

from cablab import NetCDFCubeSourceProvider


class PrecipProvider(NetCDFCubeSourceProvider):
    def __init__(self, cube_config, name='precip', dir=None):
        super(PrecipProvider, self).__init__(cube_config, name, dir)
        self.old_indices = None

    @property
    def variable_descriptors(self):
        return {
            'precipitation': {
                'source_name': 'Precip',
                'data_type': numpy.float32,
                'fill_value': -9999.0,
                'units': 'mm/day',
                # 'long_name': 'precip - v1.0',
                'standard_name': 'precipitation_flux',
                'scale_factor': 1.0,
                'add_offset': 0.0,
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
