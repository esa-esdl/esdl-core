import os
import unittest
from datetime import datetime

from cablab import CubeConfig
from cablab.providers.air_temperature import AirTemperatureProvider
from cablab.util import Config

SOURCE_DIR = Config.instance().get_cube_source_path('T2m-ECMWF\\low')


class AirTemperatureProviderTest(unittest.TestCase):
    @unittest.skipIf(not os.path.exists(SOURCE_DIR), 'test data not found: ' + SOURCE_DIR)
    def test_source_time_ranges(self):
        provider = AirTemperatureProvider(CubeConfig(end_time=datetime(2001, 6, 1, 0, 0)), SOURCE_DIR)
        provider.prepare()
        source_time_ranges = provider.get_source_time_ranges()
        self.assertEqual(1460, len(source_time_ranges))
        self.assertEqual((datetime(2001, 1, 1, 0, 0),
                          datetime(2001, 1, 1, 6, 0),
                          os.path.join(SOURCE_DIR, 'W:\\T2m-ECMWF\\low\\t2m_2001.nc'),
                          0), source_time_ranges[0])
        self.assertEqual((datetime(2001, 1, 2, 12, 0),
                          datetime(2001, 1, 2, 18, 0),
                          os.path.join(SOURCE_DIR, 'W:\\T2m-ECMWF\\low\\t2m_2001.nc'),
                          6), source_time_ranges[6])
        self.assertEqual((datetime(2001, 12, 31, 18, 0),
                          datetime(2002, 1, 1, 0, 0),
                          os.path.join(SOURCE_DIR, 'W:\\T2m-ECMWF\\low\\t2m_2001.nc'),
                          1459), source_time_ranges[1459])

    @unittest.skipIf(not os.path.exists(SOURCE_DIR), 'test data not found: ' + SOURCE_DIR)
    def test_temporal_coverage(self):
        provider = AirTemperatureProvider(CubeConfig(end_time=datetime(2001, 6, 1, 0, 0)), SOURCE_DIR)
        provider.prepare()
        self.assertEqual((datetime(2001, 1, 1, 0, 0), datetime(2002, 1, 1, 0, 0)),
                         provider.get_temporal_coverage())

    @unittest.skipIf(not os.path.exists(SOURCE_DIR), 'test data not found: ' + SOURCE_DIR)
    def test_get_images(self):
        provider = AirTemperatureProvider(CubeConfig(end_time=datetime(2001, 6, 1, 0, 0)), SOURCE_DIR)
        provider.prepare()
        images = provider.compute_variable_images(datetime(2001, 1, 1), datetime(2001, 1, 9))
        self.assertIsNotNone(images)
        self.assertTrue('t2m' in images)
        image = images['t2m']
        self.assertEqual((720, 1440), image.shape)

    @unittest.skipIf(not os.path.exists(SOURCE_DIR), 'test data not found: ' + SOURCE_DIR)
    def test_get_high_res_images(self):
        provider = AirTemperatureProvider(CubeConfig(grid_width=4320, grid_height=2160, spatial_res=1 / 12,
                                                     end_time=datetime(2001, 6, 1, 0, 0)), SOURCE_DIR)
        provider.prepare()
        images = provider.compute_variable_images(datetime(2001, 1, 1), datetime(2001, 1, 9))
        self.assertIsNotNone(images)
        self.assertTrue('t2m' in images)
        image = images['t2m']
        self.assertEqual((2160, 4320), image.shape)
