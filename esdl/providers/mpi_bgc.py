import os
from datetime import timedelta

import numpy
from esdl.cube_provider import NetCDFCubeSourceProvider
from dateutil.relativedelta import relativedelta
from netCDF4 import num2date

all_vars_descr = {'GPPall': {
    'gross_primary_productivity': {
        'source_name': 'GPPall',
        'data_type': numpy.float32,
        'fill_value': numpy.nan,
        'units': 'gC m-2 day-1',
        'long_name': 'Gross Primary Productivity',
        'references': 'Tramontana, Gianluca, et al. "Predicting carbon dioxide and energy fluxes across global '
                      'FLUXNET sites with regression algorithms." (2016).',
        'standard_name': 'gross_primary_productivity_of_carbon',
        'url': 'http://www.fluxcom.org/',
        'project_name' : 'FLUXCOM',
        'comment' : 'Gross Carbon uptake of of the ecosystem through photosynthesis',
    }},

    'TERall': {
        'terrestrial_ecosystem_respiration': {
            'source_name': 'TERall',
            'data_type': numpy.float32,
            'fill_value': numpy.nan,
            'units': 'gC m-2 day-1',
            'long_name': 'Terrestrial Ecosystem Respiration',
            'references': 'Tramontana, Gianluca, et al. "Predicting carbon dioxide and energy fluxes across global '
                          'FLUXNET sites with regression algorithms." (2016).',
            'standard_name': 'ecosystem_respiration_carbon_flux',
            'url': 'http://www.fluxcom.org/',
            'project_name' : 'FLUXCOM',
            'comment' : 'Total carbon release of the ecosystem through respiration.',
        }},
    'NEE': {
        'net_ecosystem_exchange': {
            'source_name': 'NEE',
            'data_type': numpy.float32,
            'fill_value': numpy.nan,
            'units': 'gC m-2 day-1',
            'long_name': 'Net Ecosystem Exchange',
            'references': 'Tramontana, Gianluca, et al. "Predicting carbon dioxide and energy fluxes across global '
                          'FLUXNET sites with regression algorithms." (2016).',
            'standard_name': 'net_primary_productivity_of_carbon',
            'url': 'http://www.fluxcom.org/',
            'project_name' : 'FLUXCOM',
            'comment' : 'Net carbon exchange between the ecosystem and the atmopshere.'
        }},
    'LE': {
        'latent_energy': {
            'source_name': 'LE',
            'data_type': numpy.float32,
            'fill_value': numpy.nan,
            'units': 'W m-2',
            'long_name': 'Latent Energy',
            'references': 'Tramontana, Gianluca, et al. "Predicting carbon dioxide and energy fluxes across global '
                          'FLUXNET sites with regression algorithms." (2016).',
            'standard_name': 'surface_upward_latent_heat_flux',
            'url': 'http://www.fluxcom.org/',
            'project_name' : 'FLUXCOM',
            'comment' : 'Latent heat flux from the surface.',
        }},
    'H': {
        'sensible_heat': {
            'source_name': 'H',
            'data_type': numpy.float32,
            'fill_value': numpy.nan,
            'units': 'W m-2',
            'long_name': 'Sensible Heat',
            'references': 'Tramontana, Gianluca, et al. "Predicting carbon dioxide and energy fluxes across global '
                          'FLUXNET sites with regression algorithms." (2016).',
            'standard_name': 'surface_upward_sensible_heat_flux',
            'url': 'http://www.fluxcom.org/',
            'project_name' : 'FLUXCOM',
            'comment' : 'Sensible heat flux from the surface'
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
                    for i in range(len(dates)):
                        # the following checks if the end period overlaps with the next year. If so, change the
                        # timedelta so that the period stops at the last day of the year
                        days_increment = 8 if (dates[i] + timedelta(days=8)).year == source_year else \
                            (dates[i] + timedelta(days=8) - relativedelta(years=1)).day
                        source_time_ranges.append((dates[i], dates[i] + timedelta(days=days_increment), file, i))
        return sorted(source_time_ranges, key=lambda item: item[0])
