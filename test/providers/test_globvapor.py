import os
import unittest
from datetime import datetime

from cablab import CubeConfig
from cablab.providers.globvapour import GlobVapourProvider
from cablab.util import Config

SOURCE_DIR = Config.instance().get_cube_source_path('globvapour\\GOME_SCIA_GOME2\\monthly')


class GlobVapourProviderTest(unittest.TestCase):
    @unittest.skipIf(not os.path.exists(SOURCE_DIR), 'test data not found: ' + SOURCE_DIR)
    def test_source_time_ranges(self):
        provider = GlobVapourProvider(CubeConfig(), SOURCE_DIR)
        provider.prepare()
        source_time_ranges = provider.get_source_time_ranges()
        self.assertEqual(156, len(source_time_ranges))
        self.assertEqual((datetime(1996, 1, 1, 0, 0),
                          datetime(1996, 2, 1, 0, 0),
                          os.path.join(SOURCE_DIR, '1996\\GV_GOMExxxxxxx_MM_19960101_E_3.nc'),
                          0), source_time_ranges[0])

        self.assertEqual((datetime(2006, 6, 1, 0, 0),
                          datetime(2006, 7, 1, 0, 0),
                          os.path.join(SOURCE_DIR, '2006\\SCIAxxxxxxx_L3_MM_ENV_20060630000000_E_20120214101955.nc.gz'),
                          0), source_time_ranges[125])

        self.assertEqual((datetime(2008, 12, 1, 0, 0),
                          datetime(2009, 1, 1, 0, 0),
                          os.path.join(SOURCE_DIR, '2008\\GV_GOME2xxxxxx_MM_20081201_E_3.nc'),
                          0), source_time_ranges[155])

    @unittest.skipIf(not os.path.exists(SOURCE_DIR), 'test data not found: ' + SOURCE_DIR)
    def test_temporal_coverage(self):
        provider = GlobVapourProvider(CubeConfig(), SOURCE_DIR)
        provider.prepare()
        temporal_coverage = provider.get_temporal_coverage()
        self.assertEqual((datetime(1996, 1, 1, 0, 0),
                          datetime(2009, 1, 1, 0, 0)),
                         temporal_coverage)

    @unittest.skipIf(not os.path.exists(SOURCE_DIR), 'test data not found: ' + SOURCE_DIR)
    def test_get_images(self):
        provider = GlobVapourProvider(CubeConfig(), SOURCE_DIR)
        provider.prepare()
        images = provider.compute_variable_images(datetime(2007, 1, 1), datetime(2007, 1, 9))
        self.assertIsNotNone(images)
        self.assertTrue('tcwv_res' in images)
        image = images['tcwv_res']
        self.assertEqual((720, 1440), image.shape)

    @unittest.skipIf(not os.path.exists(SOURCE_DIR), 'test data not found: ' + SOURCE_DIR)
    def test_get_high_res_images(self):
        provider = GlobVapourProvider(CubeConfig(grid_width=4320, grid_height=2160, spatial_res=1/12), SOURCE_DIR)
        provider.prepare()
        images = provider.compute_variable_images(datetime(2007, 1, 1), datetime(2007, 1, 9))
        self.assertIsNotNone(images)
        self.assertTrue('tcwv_res' in images)
        image = images['tcwv_res']
        self.assertEqual((2160, 4320), image.shape)
