from unittest import TestCase
import shutil
from datetime import datetime
import os

import numpy

from cablab import ImageProvider, CubeConfig, Cube

CUBE_DIR = 'testcube'


class CubeTest(TestCase):
    def setUp(self):
        while os.path.exists(CUBE_DIR):
            shutil.rmtree(CUBE_DIR, True)

    def tearDown(self):
        # while os.path.exists(CUBE_DIR):
        #     shutil.rmtree(CUBE_DIR, True)
        pass

    def test_update(self):
        import os

        config = CubeConfig()
        cube = Cube.create(CUBE_DIR, config)
        self.assertTrue(os.path.exists(CUBE_DIR))

        provider = ImageProviderMock(start_time=datetime(2000, 1, 1), end_time=datetime(2000, 2, 1))
        cube.update(provider)

        self.assertEqual([(datetime(2000, 1, 1, 0, 0), datetime(2000, 1, 9, 0, 0)),
                          (datetime(2000, 1, 9, 0, 0), datetime(2000, 1, 17, 0, 0)),
                          (datetime(2000, 1, 17, 0, 0), datetime(2000, 1, 25, 0, 0)),
                          (datetime(2000, 1, 25, 0, 0), datetime(2000, 2, 2, 0, 0))],
                         provider.trace)

        self.assertTrue(os.path.exists(CUBE_DIR + "/cube.config"))
        self.assertTrue(os.path.exists(CUBE_DIR + "/data/2000/2000_LAI.nc"))
        self.assertTrue(os.path.exists(CUBE_DIR + "/data/2000/2000_FAPAR.nc"))

        cube.close()

        with self.assertRaises(IOError) as ioe:
            cube.update(provider)

        cube2 = Cube.open(CUBE_DIR)
        self.assertEqual(cube.config.spatial_res, cube2.config.spatial_res)
        self.assertEqual(cube.config.temporal_res, cube2.config.temporal_res)
        self.assertEqual(cube.config.format, cube2.config.format)
        self.assertEqual(cube.config.compression, cube2.config.compression)

        provider = ImageProviderMock(start_time=datetime(2013, 1, 1), end_time=datetime(2013, 2, 1))
        cube2.update(provider)
        self.assertEqual([(datetime(2012, 12, 27, 0, 0), datetime(2013, 1, 4, 0, 0)),
                          (datetime(2013, 1, 4, 0, 0), datetime(2013, 1, 12, 0, 0)),
                          (datetime(2013, 1, 12, 0, 0), datetime(2013, 1, 20, 0, 0)),
                          (datetime(2013, 1, 20, 0, 0), datetime(2013, 1, 28, 0, 0)),
                          (datetime(2013, 1, 28, 0, 0), datetime(2013, 2, 5, 0, 0))],
                         provider.trace)

        self.assertTrue(os.path.exists(CUBE_DIR + "/data/2012/2012_LAI.nc"))
        self.assertTrue(os.path.exists(CUBE_DIR + "/data/2012/2012_FAPAR.nc"))
        self.assertTrue(os.path.exists(CUBE_DIR + "/data/2013/2013_LAI.nc"))
        self.assertTrue(os.path.exists(CUBE_DIR + "/data/2013/2013_FAPAR.nc"))

        cube2.close()


class ImageProviderMock(ImageProvider):
    def __init__(self,
                 start_time=datetime(2013, 1, 1),
                 end_time=datetime(2013, 2, 1)):
        self.start_time = start_time
        self.end_time = end_time
        self.trace = []
        self.cube_config = None
        self.lai_value = 0.1
        self.fapar_value = 0.6

    def prepare(self, cube_config):
        self.cube_config = cube_config

    def get_variable_metadata(self, variable):
        metadata = {
            'datatype': numpy.float32,
            'fill_value': 0.0,
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
        self.lai_value += 0.01
        self.fapar_value += 0.005
        image_width = self.cube_config.grid_width
        image_height = self.cube_config.grid_height
        image_shape = (image_height, image_width)
        return {'LAI': numpy.full(image_shape, self.lai_value, dtype=numpy.float32),
                'FAPAR': numpy.full(image_shape, self.fapar_value, dtype=numpy.float32)}

    def close(self):
        pass
