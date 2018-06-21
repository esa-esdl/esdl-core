import os
from datetime import timedelta

import netCDF4
import numpy

from esdl.cube_provider import NetCDFCubeSourceProvider


class SoilMoistureProvider(NetCDFCubeSourceProvider):
    def __init__(self, cube_config, name='soil_moisture', dir=None, resampling_order=None):
        super(SoilMoistureProvider, self).__init__(cube_config, name, dir, resampling_order)
        self.old_indices = None

    @property
    def variable_descriptors(self):
        return {
            'soil_moisture': {
                'source_name': 'SoilMoisture',
                'data_type': numpy.float32,
                'fill_value': -9999.0,
                'units': 'm3',
                'long_name': 'Soil Moisture',
                'standard_name': 'soil_moisture_content',
                'references': 'Liu, Y.Y., Parinussa, R.M., Dorigo, W.A., De Jeu, '
                              'R.A.M., Wagner, W., McCabe, M.F., Evans, J.P., and van Dijk, A.I.J.M. '
                              '(2012): Trend-preserving blending of passive and active microwave soil '
                              'moisture retrievals; Liu, Y.Y., Parinussa, R.M., Dorigo, W.A., De Jeu, '
                              'R.A.M., Wagner, W., van Dijk, A.I.J.M., McCabe, M.F., & Evans, J.P. '
                              '(2011): Developing an improved soil moisture dataset by blending passive '
                              'and active microwave satellite based retrievals. Hydrology and Earth System Sciences, 15, 425-436.',
                'url': 'http://www.esa-soilmoisture-cci.org',
                'comment': 'Soil moisture based on the SOilmoisture CCI project',
                'project_name' : 'SoilMoisture CCI',
            }
        }

    def compute_source_time_ranges(self):
        source_time_ranges = []
        file_names = os.listdir(self.dir_path)
        for file_name in file_names:
            if file_name.endswith('.nc.gz'):
                file = os.path.join(self.dir_path, file_name)
                dataset = self.dataset_cache.get_dataset(file)
                time = dataset.variables['time']
                # dates = netCDF4.num2date(time[:], time.units, calendar=time.calendar)
                dates = netCDF4.num2date(time[:], 'days since 1582-10-15 00:00', calendar='gregorian')
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
