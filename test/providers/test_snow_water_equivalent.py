import os
import unittest
from datetime import datetime

import numpy as np

from esdl import CubeConfig
from esdl.providers.snow_water_equivalent import SnowWaterEquivalentProvider
from test.providers.provider_test_utils import ProviderTestBase
from esdl.util import Config

SOURCE_DIR = Config.instance().get_cube_source_path('SWE')


class SnowWaterEquivalentProviderTest(ProviderTestBase):
    @unittest.skipIf(not os.path.exists(SOURCE_DIR), 'test data not found: ' + SOURCE_DIR)
    def test_source_time_ranges(self):
        provider = SnowWaterEquivalentProvider(CubeConfig(), dir=SOURCE_DIR)
        provider.prepare()
        source_time_ranges = provider.source_time_ranges
        self.assertEqual(12054, len(source_time_ranges))
        self.assert_source_time_ranges(source_time_ranges[0],
                                       datetime(1980, 1, 1, 0, 0),
                                       datetime(1980, 1, 2, 0, 0),
                                       self.get_source_dir_list(SOURCE_DIR) + ['SWE.1440.720.1980.nc'],
                                       0)
        self.assert_source_time_ranges(source_time_ranges[1000],
                                       datetime(1982, 9, 27, 0, 0),
                                       datetime(1982, 9, 28, 0, 0),
                                       self.get_source_dir_list(SOURCE_DIR) + ['SWE.1440.720.1982.nc'],
                                       269)
        self.assert_source_time_ranges(source_time_ranges[5000],
                                       datetime(1993, 9, 9, 0, 0),
                                       datetime(1993, 9, 10, 0, 0),
                                       self.get_source_dir_list(SOURCE_DIR) + ['SWE.1440.720.1993.nc'],
                                       251)
        self.assert_source_time_ranges(source_time_ranges[12053],
                                       datetime(2012, 12, 31, 0, 0),
                                       datetime(2013, 1, 1, 0, 0),
                                       self.get_source_dir_list(SOURCE_DIR) + ['SWE.1440.720.2012.nc'],
                                       365)

    @unittest.skipIf(not os.path.exists(SOURCE_DIR), 'test data not found: ' + SOURCE_DIR)
    def test_temporal_coverage(self):
        provider = SnowWaterEquivalentProvider(CubeConfig(), dir=SOURCE_DIR)
        provider.prepare()
        temporal_coverage = provider.temporal_coverage
        self.assertEqual((datetime(1980, 1, 1, 0, 0),
                          datetime(2013, 1, 1, 0, 0)),
                         temporal_coverage)

    @unittest.skipIf(not os.path.exists(SOURCE_DIR), 'test data not found: ' + SOURCE_DIR)
    def test_get_images(self):
        provider = SnowWaterEquivalentProvider(CubeConfig(), dir=SOURCE_DIR)
        provider.prepare()
        images = provider.compute_variable_images(datetime(2010, 1, 1), datetime(2010, 12, 31))
        self.assertIsNotNone(images)
        self.assertTrue('snow_water_equivalent' in images)
        image = images['snow_water_equivalent']
        self.assertEqual((720, 1440), image.shape)
        self.assertEqual(0, np.isnan(image).sum())

    @unittest.skipIf(not os.path.exists(SOURCE_DIR), 'test data not found: ' + SOURCE_DIR)
    def test_get_high_res_images(self):
        provider = SnowWaterEquivalentProvider(CubeConfig(grid_width=4320, grid_height=2160, spatial_res=1 / 12),
                                               dir=SOURCE_DIR)
        provider.prepare()
        images = provider.compute_variable_images(datetime(2010, 1, 1), datetime(2010, 12, 31))
        self.assertIsNotNone(images)
        self.assertTrue('snow_water_equivalent' in images)
        image = images['snow_water_equivalent']
        self.assertEqual((2160, 4320), image.shape)
        self.assertEqual(0, np.isnan(image).sum())
