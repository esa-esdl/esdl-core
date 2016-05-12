import os
import shutil
from datetime import datetime
from unittest import TestCase

import numpy

from cablab import CubeSourceProvider, CubeConfig, Cube, CUBE_MODEL_VERSION

CUBE_DIR = 'testcube'


class CubeConfigTest(TestCase):
    def test_validate(self):
        with self.assertRaises(ValueError):
            CubeConfig(grid_x0=1)
        with self.assertRaises(ValueError):
            CubeConfig(grid_y0=1)
        with self.assertRaises(ValueError):
            CubeConfig(grid_x0=-1)
        with self.assertRaises(ValueError):
            CubeConfig(grid_y0=-1)

    def test_model_version_is_current(self):
        config = CubeConfig()
        self.assertEqual(CUBE_MODEL_VERSION, config.model_version)

    def test_properties(self):
        config = CubeConfig()

        self.assertEqual(-180, config.easting)
        self.assertEqual(90, config.northing)
        self.assertEqual(((-180, -90), (180, 90)), config.geo_bounds)

        config = CubeConfig(grid_x0=430, grid_y0=28, grid_width=100, grid_height=100, spatial_res=0.5)
        self.assertEqual(35.0, config.easting)
        self.assertEqual(76.0, config.northing)
        self.assertEqual(((35.0, 26.0), (85.0, 76.0)), config.geo_bounds)


class CubeTest(TestCase):
    def setUp(self):
        while os.path.exists(CUBE_DIR):
            shutil.rmtree(CUBE_DIR, True)

    def tearDown(self):
        # while os.path.exists(CUBE_DIR):
        #     shutil.rmtree(CUBE_DIR, True)
        pass

    def test_update(self):
        cube = Cube.create(CUBE_DIR, CubeConfig())
        self.assertTrue(os.path.exists(CUBE_DIR))

        provider = CubeSourceProviderMock(cube.config, start_time=datetime(2001, 1, 1), end_time=datetime(2001, 2, 1))
        cube.update(provider)

        self.assertEqual([(datetime(2001, 1, 1, 0, 0), datetime(2001, 1, 9, 0, 0)),
                          (datetime(2001, 1, 9, 0, 0), datetime(2001, 1, 17, 0, 0)),
                          (datetime(2001, 1, 17, 0, 0), datetime(2001, 1, 25, 0, 0)),
                          (datetime(2001, 1, 25, 0, 0), datetime(2001, 2, 2, 0, 0))],
                         provider.trace)

        self.assertTrue(os.path.exists(CUBE_DIR + "/cube.config"))
        self.assertTrue(os.path.exists(CUBE_DIR + "/data/LAI/2001_LAI.nc"))
        self.assertTrue(os.path.exists(CUBE_DIR + "/data/FAPAR/2001_FAPAR.nc"))

        cube.close()

        with self.assertRaises(IOError):
            cube.update(provider)

        cube2 = Cube.open(CUBE_DIR)
        self.assertEqual(cube.config.spatial_res, cube2.config.spatial_res)
        self.assertEqual(cube.config.temporal_res, cube2.config.temporal_res)
        self.assertEqual(cube.config.file_format, cube2.config.file_format)
        self.assertEqual(cube.config.compression, cube2.config.compression)

        provider = CubeSourceProviderMock(cube2.config,
                                          start_time=datetime(2006, 12, 15),
                                          end_time=datetime(2007, 1, 15))
        cube2.update(provider)
        self.assertEqual([(datetime(2006, 12, 11, 0, 0), datetime(2006, 12, 19, 0, 0)),  # 8 days
                          (datetime(2006, 12, 19, 0, 0), datetime(2006, 12, 27, 0, 0)),  # 8 days
                          (datetime(2006, 12, 27, 0, 0), datetime(2007, 1, 1, 0, 0)),  # 8 days
                          (datetime(2007, 1, 1, 0, 0), datetime(2007, 1, 9, 0, 0)),  # 8 days
                          (datetime(2007, 1, 9, 0, 0), datetime(2007, 1, 17, 0, 0))],  # 8 days
                         provider.trace)

        self.assertTrue(os.path.exists(CUBE_DIR + "/data/LAI/2006_LAI.nc"))
        self.assertTrue(os.path.exists(CUBE_DIR + "/data/LAI/2007_LAI.nc"))
        self.assertTrue(os.path.exists(CUBE_DIR + "/data/FAPAR/2006_FAPAR.nc"))
        self.assertTrue(os.path.exists(CUBE_DIR + "/data/FAPAR/2007_FAPAR.nc"))

        data = cube2.data
        self.assertIsNotNone(data)
        self.assertEqual((2, 10 * 46, 720, 1440), data.shape)
        self.assertEquals({'FAPAR': 0, 'LAI': 1}, data.variable_names)

        self.assertIsNotNone(data.get_variable('LAI'))
        self.assertIs(data.get_variable('LAI'), data['LAI'])
        self.assertIs(data.get_variable('LAI'), data[1])
        self.assertIs(data.get_variable(1), data[1])
        array = data['LAI'][:, :, :]
        self.assertEqual((138, 720, 1440), array.shape)
        scalar = data['LAI'][3, 320, 720]
        self.assertEqual(numpy.float32, type(scalar))
        self.assertEqual(numpy.array([0.14], dtype=numpy.float32), scalar)

        self.assertIsNotNone(data.get_variable('FAPAR'))
        self.assertIs(data.get_variable('FAPAR'), data['FAPAR'])
        self.assertIs(data.get_variable('FAPAR'), data[0])
        self.assertIs(data.get_variable(0), data[0])
        array = data['FAPAR'][:, :, :]
        self.assertEqual((138, 720, 1440), array.shape)
        scalar = data['FAPAR'][3, 320, 720]
        self.assertEqual(numpy.array([0.62], dtype=numpy.float32), scalar)

        result = data.get('FAPAR',
                          [datetime(2001, 1, 1), datetime(2001, 2, 1)],
                          [-90, 90],
                          [-180, +180])
        self.assertEqual(1, len(result))
        self.assertEqual((4, 720, 1440), result[0].shape)

        result = data.get(['FAPAR', 'LAI'],
                          [datetime(2001, 1, 1), datetime(2001, 2, 1)],
                          [50.0, 60.0],
                          [10.0, 30.0])
        self.assertEqual(2, len(result))
        self.assertEqual((4, 40, 80), result[0].shape)
        self.assertEqual((4, 40, 80), result[1].shape)

        result = data.get(1,
                          datetime(2001, 1, 20),
                          0,
                          0)
        self.assertEqual(1, len(result))
        self.assertEqual((), result[0].shape)
        self.assertEqual(numpy.array([0.13], dtype=numpy.float32), result[0])

        result = data.get(0,
                          datetime(2001, 1, 20),
                          -12.6,
                          5.9)
        self.assertEqual(1, len(result))
        self.assertEqual((), result[0].shape)
        self.assertEqual(numpy.array([0.61500001], dtype=numpy.float32), result[0])

        result = data.get((1, 0),
                          datetime(2001, 1, 20),
                          53.4,
                          13.1)
        self.assertEqual(2, len(result))
        self.assertEqual((), result[0].shape)
        self.assertEqual((), result[1].shape)
        self.assertEqual(numpy.array([0.13], dtype=numpy.float32), result[0])
        self.assertEqual(numpy.array([0.61500001], dtype=numpy.float32), result[1])

        cube2.close()


class CubeSourceProviderMock(CubeSourceProvider):
    def __init__(self,
                 cube_config,
                 start_time=datetime(2013, 1, 1),
                 end_time=datetime(2013, 2, 1)):
        super(CubeSourceProviderMock, self).__init__(cube_config, 'test')
        self.start_time = start_time
        self.end_time = end_time
        self.trace = []
        self.lai_value = 0.1
        self.fapar_value = 0.6

    def prepare(self):
        pass

    @property
    def temporal_coverage(self):
        return self.start_time, self.end_time

    @property
    def spatial_coverage(self):
        return 0, 0, self.cube_config.grid_width, self.cube_config.grid_height

    @property
    def variable_descriptors(self):
        return {
            'LAI': {
                'data_type': numpy.float32,
                'fill_value': 0.0,
                'scale_factor': 1.0,
                'add_offset': 0.0,
            },
            'FAPAR': {
                'data_type': numpy.float32,
                'fill_value': -9999.0,
                'units': '1',
                'long_name': 'FAPAR'
            }
        }

    def compute_variable_images(self, period_start, period_end):
        self.trace.append((period_start, period_end))
        self.lai_value += 0.01
        self.fapar_value += 0.005
        image_width = self.cube_config.grid_width
        image_height = self.cube_config.grid_height
        image_shape = (image_height, image_width)
        return {'LAI': numpy.full(image_shape, self.lai_value, dtype=numpy.float32),
                'FAPAR': numpy.full(image_shape, self.fapar_value, dtype=numpy.float32)}

    def close(self):
        pass
