from datetime import datetime

import numpy
import netCDF4

from cablab import CubeSourceProvider


class BurntAreaProvider(CubeSourceProvider):
    def __init__(self):
        self.grid_width = None
        self.grid_height = None
        self.easting = None
        self.northing = None
        self.spatial_res = None
        self.start_time = None
        self.temporal_res = None
        self.variables = None
        self.source_file = 'C:\\Personal\\CabLab\\EO data\\test_cube\\BurntArea.GFED4.2009.nc'
        self.ds = None
        self.ds_variables = None

    def get_variable_metadata(self, variable):
        metadata = {
            'datatype': numpy.float32,
            'fill_value': 0,
            'units': '1',
            'long_name': variable,
            'scale_factor': 1.0,
            'add_offset': 0.0,
        }
        return metadata

    def import_dataset(self):
        self.ds = netCDF4.Dataset(self.source_file, 'r')
        self.ds_variables = self.ds.variables['BurntArea']

    def prepare(self, cube_config):
        self.grid_width = cube_config.grid_width
        self.grid_height = cube_config.grid_height
        self.easting = cube_config.easting
        self.northing = cube_config.northing
        self.spatial_res = cube_config.spatial_res
        self.start_time = cube_config.start_time
        self.temporal_res = cube_config.temporal_res
        self.variables = cube_config.variables

    def get_temporal_coverage(self):
        return datetime(2009, 1, 1), datetime(2009, 12, 31)

    def get_spatial_coverage(self):
        return -180, -90, 1440, 720

    def get_images(self, image_start_time, image_end_time):
        return {'BurntArea': self.ds_variables[image_start_time.month - 1, :, :]}

    def close(self):
        self.ds.close()
