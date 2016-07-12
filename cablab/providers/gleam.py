import datetime
import os
from datetime import timedelta
import numpy
from cablab import NetCDFCubeSourceProvider

all_vars_descr = {'E': {
    'evaporation': {
        'source_name': 'E',
        'data_type': numpy.float32,
        'fill_value': numpy.nan,
        'units': 'mm/day',
        'long_name': 'Evaporation',
        'standard_name': 'water_evaporation_flux',
        'scale_factor': 1.0,
        'add_offset': 0.0,
        'url': 'http://www.gleam.eu',
    }},
    'S': {
        'evaporative_stress': {
            'source_name': 'S',
            'data_type': numpy.float32,
            'fill_value': numpy.nan,
            'units': '',
            'long_name': 'Evaporative Stress Factor',
            'standard_name': 'evaporative_stress_factor',
            'scale_factor': 1.0,
            'add_offset': 0.0,
            'url': 'http://www.gleam.eu',
        }},
    'Ep': {
        'potential_evaporation': {
            'source_name': 'Ep',
            'data_type': numpy.float32,
            'fill_value': numpy.nan,
            'units': 'mm/day',
            'long_name': 'Potential Evaporation',
            'standard_name': 'potential_water_evaporation_flux',
            'scale_factor': 1.0,
            'add_offset': 0.0,
            'url': 'http://www.gleam.eu',
        }},
    'Ei': {
        'interception_loss': {
            'source_name': 'Ei',
            'data_type': numpy.float32,
            'fill_value': numpy.nan,
            'units': 'mm/day',
            'long_name': 'Interception Loss',
            'standard_name': 'interception_loss',
            'scale_factor': 1.0,
            'add_offset': 0.0,
            'url': 'http://www.gleam.eu',
        }},
    'SMroot': {
        'root_moisture': {
            'source_name': 'SMroot',
            'data_type': numpy.float32,
            'fill_value': numpy.nan,
            'units': 'm3/m3',
            'long_name': 'Root-Zone Soil Moisture',
            'standard_name': 'soil_moisture_content',
            'scale_factor': 1.0,
            'add_offset': 0.0,
            'url': 'http://www.gleam.eu',
        }},
    'SMsurf': {
        'surface_moisture': {
            'source_name': 'SMsurf',
            'data_type': numpy.float32,
            'fill_value': numpy.nan,
            'units': 'mm3/mm3',
            'long_name': 'Surface Soil Moisture',
            'standard_name': 'soil_moisture_content',
            'scale_factor': 1.0,
            'add_offset': 0.0,
            'url': 'http://www.gleam.eu',
        }},
    'Eb': {
        'bare_soil_evaporation': {
            'source_name': 'Eb',
            'data_type': numpy.float32,
            'fill_value': numpy.nan,
            'units': 'mm/day',
            'long_name': 'Bare Soil Evaporation',
            'standard_name': 'bare_soil_water_evaporation_flux',
            'scale_factor': 1.0,
            'add_offset': 0.0,
            'url': 'http://www.gleam.eu',
        }},
    'Es': {
        'snow_sublimation': {
            'source_name': 'Es',
            'data_type': numpy.float32,
            'fill_value': numpy.nan,
            'units': 'mm/day',
            'long_name': 'Snow Sublimation',
            'standard_name': 'snow_sublimation_flux',
            'scale_factor': 1.0,
            'add_offset': 0.0,
            'url': 'http://www.gleam.eu',
        }},
    'Et': {
        'transpiration': {
            'source_name': 'Et',
            'data_type': numpy.float32,
            'fill_value': numpy.nan,
            'units': 'mm/day',
            'long_name': 'Transpiration',
            'standard_name': 'transpiration_flux',
            'scale_factor': 1.0,
            'add_offset': 0.0,
            'url': 'http://www.gleam.eu',
        }},
    'Ew': {
        'open_water_evaporation': {
            'source_name': 'Ew',
            'data_type': numpy.float32,
            'fill_value': numpy.nan,
            'units': 'mm/day',
            'long_name': 'Open-water Evaporation',
            'standard_name': 'water_evaporation_flux',
            'scale_factor': 1.0,
            'add_offset': 0.0,
            'url': 'http://www.gleam.eu',
        }},

}


class GleamProvider(NetCDFCubeSourceProvider):
    def __init__(self, cube_config, name='GLEAM', dir=None, resampling_order=None, var=None):
        super(GleamProvider, self).__init__(cube_config, name, dir, resampling_order)
        self.var_name = var
        self.old_indices = None

    @property
    def variable_descriptors(self):
        return all_vars_descr[self.var_name]

    def compute_source_time_ranges(self):
        source_time_ranges = []
        for root, sub_dirs, files in os.walk(self.dir_path):
            for sub_dir in sub_dirs:
                source_year = int(sub_dir)
                if self.cube_config.start_time.year <= source_year <= self.cube_config.end_time.year:
                    sub_dir_path = os.path.join(self.dir_path, sub_dir)
                    file_names = os.listdir(sub_dir_path)
                    for file_name in file_names:
                        if self.var_name + '_' in file_name:
                            file = os.path.join(self.dir_path, sub_dir, file_name).replace("\\", "/")
                            dataset = self.dataset_cache.get_dataset(file)
                            year = dataset.variables['DATE'][0, :].astype(int)
                            month = dataset.variables['DATE'][1, :].astype(int)
                            day = dataset.variables['DATE'][2, :].astype(int)
                            self.dataset_cache.close_dataset(file)
                            dates = [datetime.datetime(year[i], month[i], day[i]) for i in range(len(year))]
                            cnt = 0
                            for time in dates:
                                if self.cube_config.start_time <= time <= self.cube_config.end_time:
                                    source_time_ranges.append((time, time + timedelta(days=1), file, cnt))
                                    cnt += 1

        return sorted(source_time_ranges, key=lambda item: item[0])

    def transform_source_image(self, source_image):
        """
        Transforms the source image, here by rotating and flipping.
        :param source_image: 2D image
        :return: source_image
        """
        return numpy.fliplr(numpy.rot90(source_image, 3))
