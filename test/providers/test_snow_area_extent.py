import os
import unittest
from datetime import datetime

from esdl import CubeConfig
from esdl.providers.snow_area_extent import SnowAreaExtentProvider
from test.providers.provider_test_utils import ProviderTestBase
from esdl.util import Config

SOURCE_DIR = Config.instance().get_cube_source_path('SnowAreaExtent')


class SnowAreaExtentProviderTest(ProviderTestBase):
    @unittest.skipIf(not os.path.exists(SOURCE_DIR), 'test data not found: ' + SOURCE_DIR)
    def test_source_time_ranges(self):
        provider = SnowAreaExtentProvider(CubeConfig(), dir=SOURCE_DIR, resampling_order="space_first")
        provider.prepare()
        source_time_ranges = provider.source_time_ranges
        self.assertEqual(120, len(source_time_ranges))
        self.assert_source_time_ranges(source_time_ranges[0],
                                       datetime(2003, 1, 1, 0, 0, 0, 33),
                                       datetime(2003, 2, 1, 0, 0, 0, 33),
                                       self.get_source_dir_list(SOURCE_DIR) + ['MFSC.36000.18000.2003.nc'],
                                       0)
        self.assert_source_time_ranges(source_time_ranges[1],
                                       datetime(2003, 2, 1, 0, 0, 0, 33),
                                       datetime(2003, 3, 1, 0, 0, 0, 33),
                                       self.get_source_dir_list(SOURCE_DIR) + ['MFSC.36000.18000.2003.nc'],
                                       1)
        self.assert_source_time_ranges(source_time_ranges[6],
                                       datetime(2003, 7, 1, 0, 0, 0, 33),
                                       datetime(2003, 8, 1, 0, 0, 0, 33),
                                       self.get_source_dir_list(SOURCE_DIR) + ['MFSC.36000.18000.2003.nc'],
                                       6)
        self.assert_source_time_ranges(source_time_ranges[119],
                                       datetime(2012, 12, 1, 0, 0, 0, 33),
                                       datetime(2013, 1, 1, 0, 0, 0, 33),
                                       self.get_source_dir_list(SOURCE_DIR) + ['MFSC.36000.18000.2012.nc'],
                                       11)

    @unittest.skipIf(not os.path.exists(SOURCE_DIR), 'test data not found: ' + SOURCE_DIR)
    def test_temporal_coverage(self):
        provider = SnowAreaExtentProvider(CubeConfig(), dir=SOURCE_DIR, resampling_order="space_first")
        provider.prepare()
        temporal_coverage = provider.temporal_coverage
        self.assertEqual((datetime(2003, 1, 1, 0, 0, 0, 33),
                          datetime(2013, 1, 1, 0, 0, 0, 33)),
                         temporal_coverage)

    @unittest.skipIf(not os.path.exists(SOURCE_DIR), 'test data not found: ' + SOURCE_DIR)
    def test_get_images(self):
        provider = SnowAreaExtentProvider(CubeConfig(), dir=SOURCE_DIR, resampling_order="space_first")
        provider.prepare()
        images = provider.compute_variable_images(datetime(2003, 1, 1), datetime(2003, 2, 11))
        self.assertIsNotNone(images)
        self.assertTrue('fractional_snow_cover' in images)
        image = images['fractional_snow_cover']
        self.assertEqual((720, 1440), image.shape)

    @unittest.skipIf(not os.path.exists(SOURCE_DIR), 'test data not found: ' + SOURCE_DIR)
    def test_get_images_from_single_time_period(self):
        provider = SnowAreaExtentProvider(CubeConfig(), dir=SOURCE_DIR, resampling_order="space_first")
        provider.prepare()
        images = provider.compute_variable_images(datetime(2003, 1, 1), datetime(2003, 1, 31))
        self.assertIsNotNone(images)
        self.assertTrue('fractional_snow_cover' in images)
        image = images['fractional_snow_cover']
        self.assertEqual((720, 1440), image.shape)

    @unittest.skipIf(not os.path.exists(SOURCE_DIR), 'test data not found: ' + SOURCE_DIR)
    def test_get_high_res_images_from_single_time_period(self):
        provider = SnowAreaExtentProvider(CubeConfig(grid_width=4320, grid_height=2160, spatial_res=1 / 12),
                                          dir=SOURCE_DIR, resampling_order="space_first")
        provider.prepare()
        images = provider.compute_variable_images(datetime(2003, 1, 1), datetime(2003, 1, 31))
        self.assertIsNotNone(images)
        self.assertTrue('fractional_snow_cover' in images)
        image = images['fractional_snow_cover']
        self.assertEqual((2160, 4320), image.shape)
