from datetime import datetime
import os
import unittest

from cablab import CubeConfig
from cablab.providers.snow_area_extent import SnowAreaExtentProvider
from cablab.util import Config

SOURCE_DIR = Config.instance().get_cube_source_path('SnowAreaExtent')


class SnowAreaExtentProviderTest(unittest.TestCase):
    @unittest.skipIf(not os.path.exists(SOURCE_DIR), 'test data not found: ' + SOURCE_DIR)
    def test_source_time_ranges(self):
        provider = SnowAreaExtentProvider(CubeConfig(), SOURCE_DIR)
        provider.prepare()
        source_time_ranges = provider.get_source_time_ranges()
        self.assertEqual(120, len(source_time_ranges))
        self.assertEqual((datetime(2003, 1, 1, 0, 0, 0, 33),
                          datetime(2003, 2, 1, 0, 0, 0, 33),
                          os.path.join(SOURCE_DIR, 'MFSC.36000.18000.2003.nc'),
                          0), source_time_ranges[0])
        self.assertEqual((datetime(2003, 2, 1, 0, 0, 0, 33),
                          datetime(2003, 3, 1, 0, 0, 0, 33),
                          os.path.join(SOURCE_DIR, 'MFSC.36000.18000.2003.nc'),
                          1), source_time_ranges[1])
        self.assertEqual((datetime(2003, 7, 1, 0, 0, 0, 33),
                          datetime(2003, 8, 1, 0, 0, 0, 33),
                          os.path.join(SOURCE_DIR, 'MFSC.36000.18000.2003.nc'),
                          6), source_time_ranges[6])
        self.assertEqual((datetime(2012, 12, 1, 0, 0, 0, 33),
                          datetime(2013, 1, 1, 0, 0, 0, 33),
                          os.path.join(SOURCE_DIR, 'MFSC.36000.18000.2012.nc'),
                          11), source_time_ranges[119])

    @unittest.skipIf(not os.path.exists(SOURCE_DIR), 'test data not found: ' + SOURCE_DIR)
    def test_temporal_coverage(self):
        provider = SnowAreaExtentProvider(CubeConfig(), SOURCE_DIR)
        provider.prepare()
        temporal_coverage = provider.temporal_coverage
        self.assertEqual((datetime(2003, 1, 1, 0, 0, 0, 33),
                          datetime(2013, 1, 1, 0, 0, 0, 33)),
                         temporal_coverage)

    @unittest.skipIf(not os.path.exists(SOURCE_DIR), 'test data not found: ' + SOURCE_DIR)
    def test_get_images(self):
        provider = SnowAreaExtentProvider(CubeConfig(), SOURCE_DIR)
        provider.prepare()
        images = provider.compute_variable_images(datetime(2003, 1, 1), datetime(2003, 2, 11))
        self.assertIsNotNone(images)
        self.assertTrue('MFSC' in images)
        image = images['MFSC']
        self.assertEqual((720, 1440), image.shape)

    @unittest.skipIf(not os.path.exists(SOURCE_DIR), 'test data not found: ' + SOURCE_DIR)
    def test_get_images_from_single_time_period(self):
        provider = SnowAreaExtentProvider(CubeConfig(), SOURCE_DIR)
        provider.prepare()
        images = provider.compute_variable_images(datetime(2003, 1, 1), datetime(2003, 1, 31))
        self.assertIsNotNone(images)
        self.assertTrue('MFSC' in images)
        image = images['MFSC']
        self.assertEqual((720, 1440), image.shape)

    @unittest.skipIf(not os.path.exists(SOURCE_DIR), 'test data not found: ' + SOURCE_DIR)
    def test_get_high_res_images_from_single_time_period(self):
        provider = SnowAreaExtentProvider(CubeConfig(grid_width=4320, grid_height=2160, spatial_res=1 / 12), SOURCE_DIR)
        provider.prepare()
        images = provider.compute_variable_images(datetime(2003, 1, 1), datetime(2003, 1, 31))
        self.assertIsNotNone(images)
        self.assertTrue('MFSC' in images)
        image = images['MFSC']
        self.assertEqual((2160, 4320), image.shape)
