import os
import unittest
from datetime import datetime

from cablab import CubeConfig
from cablab.providers.soil_moisture import SoilMoistureProvider
from cablab.util import Config

SOURCE_DIR = Config.instance().get_cube_source_path('ECV_sm')


class SoilMoistureProviderTest(unittest.TestCase):
    @unittest.skipIf(not os.path.exists(SOURCE_DIR), 'test data not found: ' + SOURCE_DIR)
    def test_source_time_ranges(self):
        provider = SoilMoistureProvider(CubeConfig(), dir=SOURCE_DIR)
        provider.prepare()
        source_time_ranges = provider.source_time_ranges
        self.assertEqual(12784, len(source_time_ranges))
        self.assertEqual((datetime(1979, 1, 1, 0, 0, 0, 33),
                          datetime(1979, 1, 2, 0, 0, 0, 33),
                          os.path.join(SOURCE_DIR, 'SoilMoisture.ESACCI-L3S.1979.v2_1.nc.gz'),
                          0), source_time_ranges[0])
        self.assertEqual((datetime(1979, 1, 7, 0, 0, 0, 33),
                          datetime(1979, 1, 8, 0, 0, 0, 33),
                          os.path.join(SOURCE_DIR, 'SoilMoisture.ESACCI-L3S.1979.v2_1.nc.gz'),
                          6), source_time_ranges[6])
        self.assertEqual((datetime(2013, 12, 31, 0, 0, 0, 33),
                          datetime(2014, 1, 31, 0, 0, 0, 33),
                          os.path.join(SOURCE_DIR, 'SoilMoisture.ESACCI-L3S.2013.v2_1.nc.gz'),
                          364), source_time_ranges[12783])

    @unittest.skipIf(not os.path.exists(SOURCE_DIR), 'test data not found: ' + SOURCE_DIR)
    def test_temporal_coverage(self):
        provider = SoilMoistureProvider(CubeConfig(), dir=SOURCE_DIR)
        provider.prepare()
        self.assertEqual((datetime(1979, 1, 1, 0, 0, 0, 33), datetime(2014, 1, 31, 0, 0, 0, 33)),
                         provider.temporal_coverage)

    @unittest.skipIf(not os.path.exists(SOURCE_DIR), 'test data not found: ' + SOURCE_DIR)
    def test_get_images(self):
        provider = SoilMoistureProvider(CubeConfig(), dir=SOURCE_DIR)
        provider.prepare()
        images = provider.compute_variable_images(datetime(1996, 1, 1), datetime(1996, 1, 9))
        self.assertIsNotNone(images)
        self.assertTrue('soil_moisture' in images)
        image = images['soil_moisture']
        self.assertEqual((720, 1440), image.shape)

    @unittest.skipIf(not os.path.exists(SOURCE_DIR), 'test data not found: ' + SOURCE_DIR)
    def test_get_high_res_images(self):
        provider = SoilMoistureProvider(CubeConfig(grid_width=4320, grid_height=2160, spatial_res=1 / 12),
                                        dir=SOURCE_DIR)
        provider.prepare()
        images = provider.compute_variable_images(datetime(1996, 1, 1), datetime(1996, 1, 9))
        self.assertIsNotNone(images)
        self.assertTrue('soil_moisture' in images)
        image = images['soil_moisture']
        self.assertEqual((2160, 4320), image.shape)
