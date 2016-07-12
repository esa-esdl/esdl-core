import os
import unittest
from datetime import datetime

from cablab import CubeConfig
from cablab.providers import GleamProvider
from cablab.util import Config

SOURCE_DIR = Config.instance().get_cube_source_path('GLEAM/v3a_BETA/')

class GleamProviderTest(unittest.TestCase):
    @unittest.skipIf(not os.path.exists(SOURCE_DIR), 'test data not found: ' + SOURCE_DIR)
    def test_source_time_ranges(self):
        provider = GleamProvider(CubeConfig(end_time=datetime(2001, 12, 31, 23, 0)), dir=SOURCE_DIR, var = "E" )
        provider.prepare()
        source_time_ranges = provider.source_time_ranges
        self.assertEqual(365, len(source_time_ranges))
        self.assertEqual((datetime(2001, 1, 4, 0, 0),datetime(2001, 1, 5, 0, 0),
                          os.path.join(SOURCE_DIR, '2001/E_2001_GLEAM_v3a_BETA.nc'),3), source_time_ranges[3])
        self.assertEqual((datetime(2001, 12, 31, 0, 0),datetime(2002, 1, 1, 0, 0),
                          os.path.join(SOURCE_DIR, '2001/E_2001_GLEAM_v3a_BETA.nc'),364), source_time_ranges[364])

    @unittest.skipIf(not os.path.exists(SOURCE_DIR), 'test data not found: ' + SOURCE_DIR)

    def test_temporal_coverage(self):
        provider = GleamProvider(CubeConfig(end_time=datetime(2001, 12, 31, 23, 0)), dir=SOURCE_DIR,  var = "S" )
        provider.prepare()
        self.assertEqual((datetime(2001, 1, 1, 0, 0), datetime(2002, 1, 1, 0, 0)),
                         provider.temporal_coverage)

    @unittest.skipIf(not os.path.exists(SOURCE_DIR), 'test data not found: ' + SOURCE_DIR)

    def test_get_images(self):
        provider = GleamProvider(CubeConfig(end_time=datetime(2001, 12, 31, 23, 0)), dir=SOURCE_DIR, var = "S")
        provider.prepare()
        images = provider.compute_variable_images(datetime(2001, 1, 1), datetime(2001, 1, 9))
        self.assertIsNotNone(images)
        self.assertTrue('evaporative_stress' in images)
        image = images['evaporative_stress']
        self.assertEqual((720, 1440), image.shape)

    @unittest.skipIf(not os.path.exists(SOURCE_DIR), 'test data not found: ' + SOURCE_DIR)

    def test_get_high_res_images(self):
        provider = GleamProvider(CubeConfig(grid_width=4320, grid_height=2160, spatial_res=1 / 12, end_time=datetime(2001, 12, 31, 23, 0)), dir=SOURCE_DIR, var = "S")
        provider.prepare()
        images = provider.compute_variable_images(datetime(2001, 1, 1), datetime(2001, 1, 9))
        self.assertIsNotNone(images)
        self.assertTrue('evaporative_stress' in images)
        image = images['evaporative_stress']
        self.assertEqual((2160, 4320), image.shape)