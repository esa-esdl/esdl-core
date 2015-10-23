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

        self.assertTrue(os.path.exists(base_dir + "/LAI"))
        self.assertTrue(os.path.exists(base_dir + "/FAPAR"))

        self.assertEqual([(datetime(2000, 1, 1, 0, 0), datetime(2000, 1, 9, 0, 0)),
                          (datetime(2000, 1, 9, 0, 0), datetime(2000, 1, 17, 0, 0)),
                          (datetime(2000, 1, 17, 0, 0), datetime(2000, 1, 25, 0, 0)),
                          (datetime(2000, 1, 25, 0, 0), datetime(2000, 2, 2, 0, 0))],
                         provider.trace)

        self.assertTrue(os.path.exists(base_dir + "/LAI/LAI_2000-01-01_00-00-00_2000-01-09_00-00-00.npy"))
        self.assertTrue(os.path.exists(base_dir + "/LAI/LAI_2000-01-09_00-00-00_2000-01-17_00-00-00.npy"))
        self.assertTrue(os.path.exists(base_dir + "/LAI/LAI_2000-01-17_00-00-00_2000-01-25_00-00-00.npy"))
        self.assertTrue(os.path.exists(base_dir + "/LAI/LAI_2000-01-25_00-00-00_2000-02-02_00-00-00.npy"))
        self.assertTrue(os.path.exists(base_dir + "/FAPAR/FAPAR_2000-01-01_00-00-00_2000-01-09_00-00-00.npy"))
        self.assertTrue(os.path.exists(base_dir + "/FAPAR/FAPAR_2000-01-09_00-00-00_2000-01-17_00-00-00.npy"))
        self.assertTrue(os.path.exists(base_dir + "/FAPAR/FAPAR_2000-01-17_00-00-00_2000-01-25_00-00-00.npy"))
        self.assertTrue(os.path.exists(base_dir + "/FAPAR/FAPAR_2000-01-25_00-00-00_2000-02-02_00-00-00.npy"))

        provider = MyLaiProvider(start_time=datetime(2013, 1, 1), end_time=datetime(2013, 2, 1))
        cube.update(provider)
        self.assertEqual([(datetime(2012, 12, 27, 0, 0), datetime(2013, 1, 4, 0, 0)),
                          (datetime(2013, 1, 4, 0, 0), datetime(2013, 1, 12, 0, 0)),
                          (datetime(2013, 1, 12, 0, 0), datetime(2013, 1, 20, 0, 0)),
                          (datetime(2013, 1, 20, 0, 0), datetime(2013, 1, 28, 0, 0)),
                          (datetime(2013, 1, 28, 0, 0), datetime(2013, 2, 5, 0, 0))],
                         provider.trace)


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
