import os
import unittest
from datetime import datetime

from cablab import CubeConfig
from cablab.providers.snow_water_equivalent import SnowWaterEquivalentProvider
from cablab.util import Config

SOURCE_DIR = Config.instance().get_cube_source_path('SWE')


class SnowWaterEquivalentProviderTest(unittest.TestCase):
    @unittest.skipIf(not os.path.exists(SOURCE_DIR), 'test data not found: ' + SOURCE_DIR)
    def test_source_time_ranges(self):
        provider = SnowWaterEquivalentProvider(CubeConfig(), SOURCE_DIR)
        provider.prepare()
        source_time_ranges = provider.get_source_time_ranges()
        self.assertEqual(12054, len(source_time_ranges))
        self.assertEqual((datetime(1980, 1, 1, 0, 0),
                          datetime(1980, 1, 2, 0, 0),
                          os.path.join(SOURCE_DIR, 'SWE.1440.720.1980.nc'),
                          0), source_time_ranges[0])
        self.assertEqual((datetime(1982, 9, 27, 0, 0),
                          datetime(1982, 9, 28, 0, 0),
                          os.path.join(SOURCE_DIR, 'SWE.1440.720.1982.nc'),
                          269), source_time_ranges[1000])
        self.assertEqual((datetime(1993, 9, 9, 0, 0),
                          datetime(1993, 9, 10, 0, 0),
                          os.path.join(SOURCE_DIR, 'SWE.1440.720.1993.nc'),
                          251), source_time_ranges[5000])
        self.assertEqual((datetime(2012, 12, 31, 0, 0),
                          datetime(2013, 1, 1, 0, 0),
                          os.path.join(SOURCE_DIR, 'SWE.1440.720.2012.nc'),
                          365), source_time_ranges[12053])

    @unittest.skipIf(not os.path.exists(SOURCE_DIR), 'test data not found: ' + SOURCE_DIR)
    def test_temporal_coverage(self):
        provider = SnowWaterEquivalentProvider(CubeConfig(), SOURCE_DIR)
        provider.prepare()
        temporal_coverage = provider.get_temporal_coverage()
        self.assertEqual((datetime(1980, 1, 1, 0, 0),
                          datetime(2013, 1, 1, 0, 0)),
                         temporal_coverage)

    @unittest.skipIf(not os.path.exists(SOURCE_DIR), 'test data not found: ' + SOURCE_DIR)
    def test_get_images(self):
        provider = SnowWaterEquivalentProvider(CubeConfig(), SOURCE_DIR)
        provider.prepare()
        images = provider.compute_variable_images(datetime(2010, 1, 1), datetime(2010, 12, 31))
        self.assertIsNotNone(images)
        self.assertTrue('SWE' in images)
        image = images['SWE']
        self.assertEqual((720, 1440), image.shape)
