import os
from datetime import timedelta
import numpy
from netCDF4 import num2date
from cablab import NetCDFCubeSourceProvider

all_vars_descr = {'GPPall': {
    'gross_primary_productivity': {
        'source_name': 'GPPall',
        'data_type': numpy.float32,
        'fill_value': numpy.nan,
        'units': 'someunit',
        'long_name': 'Gross Primary Productivity',
        'standard_name': 'gross_primary_production',
        'scale_factor': 1.0,
        'add_offset': 0.0,
        'url': 'https://www.bgc-jena.mpg.de',
    }},

    'TERall': {
        'terrestrial_ecosystem_respiration': {
            'source_name': 'TERall',
            'data_type': numpy.float32,
            'fill_value': numpy.nan,
            'units': 'someunit',
            'long_name': 'Terrestrial Ecosystem Respiration',
            'standard_name': 'put_name_here',
            'scale_factor': 1.0,
            'add_offset': 0.0,
            'url': 'https://www.bgc-jena.mpg.de',
        }},
    'NEE': {
        'net_ecosystem_exchange': {
            'source_name': 'NEE',
            'data_type': numpy.float32,
            'fill_value': numpy.nan,
            'units': 'someunit',
            'long_name': 'Net Ecosystem Exchange',
            'standard_name': 'put_name_here',
            'scale_factor': 1.0,
            'add_offset': 0.0,
            'url': 'https://www.bgc-jena.mpg.de',
        }},
    'LE': {
        'latent_energy': {
            'source_name': 'LE',
            'data_type': numpy.float32,
            'fill_value': numpy.nan,
            'units': 'someunit',
            'long_name': 'Latent Energy',
            'standard_name': 'put_name_here',
            'scale_factor': 1.0,
            'add_offset': 0.0,
            'url': 'https://www.bgc-jena.mpg.de',
        }},
    'H': {
        'sensible_heat': {
            'source_name': 'H',
            'data_type': numpy.float32,
            'fill_value': numpy.nan,
            'units': 'someunit',
            'long_name': 'Sensible Heat',
            'standard_name': 'put_name_here',
            'scale_factor': 1.0,
            'add_offset': 0.0,
            'url': 'https://www.bgc-jena.mpg.de',
        }},
}


class MPIBGCProvider(NetCDFCubeSourceProvider):
    def __init__(self, cube_config, name='MPIBGC', dir=None, resampling_order=None, var=None):
        super(MPIBGCProvider, self).__init__(cube_config, name, dir, resampling_order)
        self.var_name = var
        self.old_indices = None

    @property
    def variable_descriptors(self):
        return all_vars_descr[self.var_name]

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
                    dates = num2date(times[:], 'days since 1582-10-15 00:00:0.0', calendar='gregorian')
                    self.dataset_cache.close_dataset(file)
                    source_time_ranges += [(dates[i], dates[i] + timedelta(days=8), file, i) for i in range(len(dates))]
        return sorted(source_time_ranges, key=lambda item: item[0])
