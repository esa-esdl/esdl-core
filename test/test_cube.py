from unittest import TestCase
import shutil
from datetime import datetime

from cablab import ImageProvider, CubeConfig, Cube


class CubeTest(TestCase):
    def test_update(self):
        import os

        base_dir = 'testcube'
        if os.path.exists(base_dir):
            shutil.rmtree(base_dir, True)
        self.assertFalse(os.path.exists(base_dir))

        config = CubeConfig()
        cube = Cube.create(config, base_dir)
        self.assertTrue(os.path.exists(base_dir))

        provider = MyLaiProvider(start_time=datetime(2000, 1, 1), end_time=datetime(2000, 2, 1))
        cube.update(provider)

        self.assertTrue(os.path.exists(base_dir + "/data/2000"))

        self.assertEqual([(datetime(2000, 1, 1, 0, 0), datetime(2000, 1, 9, 0, 0)),
                          (datetime(2000, 1, 9, 0, 0), datetime(2000, 1, 17, 0, 0)),
                          (datetime(2000, 1, 17, 0, 0), datetime(2000, 1, 25, 0, 0)),
                          (datetime(2000, 1, 25, 0, 0), datetime(2000, 2, 2, 0, 0))],
                         provider.trace)

        self.assertTrue(os.path.exists(base_dir + "/cube.config"))
        self.assertTrue(os.path.exists(base_dir + "/data/2000/2000_LAI.nc"))
        self.assertTrue(os.path.exists(base_dir + "/data/2000/2000_FAPAR.nc"))

        provider = MyLaiProvider(start_time=datetime(2013, 1, 1), end_time=datetime(2013, 2, 1))
        cube.update(provider)
        self.assertEqual([(datetime(2012, 12, 27, 0, 0), datetime(2013, 1, 4, 0, 0)),
                          (datetime(2013, 1, 4, 0, 0), datetime(2013, 1, 12, 0, 0)),
                          (datetime(2013, 1, 12, 0, 0), datetime(2013, 1, 20, 0, 0)),
                          (datetime(2013, 1, 20, 0, 0), datetime(2013, 1, 28, 0, 0)),
                          (datetime(2013, 1, 28, 0, 0), datetime(2013, 2, 5, 0, 0))],
                         provider.trace)

    def test_burnt_area_provider(self):
        import os

        base_dir = 'testcube'
        if os.path.exists(base_dir):
            shutil.rmtree(base_dir, True)
        self.assertFalse(os.path.exists(base_dir))

        config = CubeConfig()
        cube = Cube.create(config, base_dir)
        self.assertTrue(os.path.exists(base_dir))

        provider = BurntAreaProvider()
        provider.import_dataset()
        provider.prepare(config)

        cube.update(provider)

import numpy


class MyLaiProvider(ImageProvider):
    def __init__(self,
                 start_time=datetime(2013, 1, 1),
                 end_time=datetime(2013, 2, 1)):
        self.start_time = start_time
        self.end_time = end_time
        self.trace = []
        self.cube_config = None

    def prepare(self, cube_config):
        self.cube_config = cube_config

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

    def get_temporal_coverage(self):
        return self.start_time, self.end_time

    def get_spatial_coverage(self):
        return 0, 0, self.cube_config.grid_width, self.cube_config.grid_height

    def get_images(self, image_start_time, image_end_time):
        self.trace.append((image_start_time, image_end_time))
        return {'LAI': numpy.zeros((self.cube_config.grid_height, self.cube_config.grid_width), dtype=numpy.float32),
                'FAPAR': numpy.zeros((self.cube_config.grid_height, self.cube_config.grid_width), dtype=numpy.float32)}

    def close(self):
        pass


import netCDF4
import cablab


class BurntAreaProvider(ImageProvider):
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

    def import_dataset(self):
        self.ds = netCDF4.Dataset(self.source_file, 'r')
        self.ds_variables = self.ds.variables['BurntArea']
        ds_time = self.ds.variables['time']
        print(ds_time.shape)
        print(len(ds_time))
        print(ds_time[0])
        print(cablab.num2date_gregorian(155663.00000000047))

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
