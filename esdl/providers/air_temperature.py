import os
from datetime import timedelta

import netCDF4
import numpy

from esdl.cube_provider import NetCDFCubeSourceProvider


class AirTemperatureProvider(NetCDFCubeSourceProvider):
    def __init__(self, cube_config, name='air_temperature', dir=None, resampling_order=None):
        super(AirTemperatureProvider, self).__init__(cube_config, name, dir, resampling_order)
        self.old_indices = None

    @property
    def variable_descriptors(self):
        return {
            'air_temperature_2m': {
                'source_name': 't2m',
                'data_type': numpy.float32,
                'fill_value': -32767,
                'units': 'K',
                'long_name': '2 metre temperature',
                'references': 'Dee, D.P. et al. 2011 http://onlinelibrary.wiley.com/doi/10.1002/qj.828/abstract',
                'comment': 'Air temperature at 2m from the ERAInterim reanalysis product.',
                'url': 'http://www.ecmwf.int/en/research/climate-reanalysis/era-interim',
                'project_name' : 'ERAInterim',
            }
        }

    def compute_source_time_ranges(self):
        source_time_ranges = []
        file_names = os.listdir(self.dir_path)
        for file_name in file_names:
            if '.nc' in file_name:
                source_year = int(file_name.replace('.nc', '').split('_')[1])
                if self.cube_config.start_time.year <= source_year <= self.cube_config.end_time.year:
                    file = os.path.join(self.dir_path, file_name).replace("\\", "/")
                    dataset = self.dataset_cache.get_dataset(file)
                    times = dataset.variables['time']
                    dates = netCDF4.num2date(times[:], 'hours since 1900-01-01 00:00:0.0', calendar='gregorian')
                    self.dataset_cache.close_dataset(file)
                    source_time_ranges += [(dates[i], dates[i] + timedelta(hours=12), file, i) for i in
                                           range(len(dates))]
        return sorted(source_time_ranges, key=lambda item: item[0])

    def transform_source_image(self, source_image):
        return numpy.roll(source_image, 720, axis=1)
