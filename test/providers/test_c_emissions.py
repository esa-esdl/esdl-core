import os
import unittest
from datetime import datetime

from cablab import CubeConfig
from cablab.providers import CEmissionsProvider
from cablab.util import Config

SOURCE_DIR = Config.instance().get_cube_source_path('Fire_C_Emissions')


class CEmissionsProviderTest(unittest.TestCase):
    @unittest.skipIf(not os.path.exists(SOURCE_DIR), 'test data not found: ' + SOURCE_DIR)
    def test_source_time_ranges(self):
        provider = CEmissionsProvider(CubeConfig(), dir=SOURCE_DIR)
        provider.prepare()
        source_time_ranges = provider.source_time_ranges
        self.assertEqual(120, len(source_time_ranges))
        self.assertEqual((datetime(2001, 1, 1, 0, 0),
                          datetime(2001, 2, 1, 0, 0),
                          os.path.join(SOURCE_DIR, 'fire_C_Emissions.nc'),
                          0), source_time_ranges[0])
        self.assertEqual((datetime(2001, 12, 1, 0, 0),
                          datetime(2002, 1, 1, 0, 0),
                          os.path.join(SOURCE_DIR, 'fire_C_Emissions.nc'),
                          11), source_time_ranges[11])
        self.assertEqual((datetime(2010, 12, 1, 0, 0),
                          datetime(2011, 1, 1, 0, 0),
                          os.path.join(SOURCE_DIR, 'fire_C_Emissions.nc'),
                          119), source_time_ranges[119])

    @unittest.skipIf(not os.path.exists(SOURCE_DIR), 'test data not found: ' + SOURCE_DIR)
    def test_temporal_coverage(self):
        provider = CEmissionsProvider(CubeConfig(), dir=SOURCE_DIR)
        provider.prepare()
        self.assertEqual((datetime(2001, 1, 1, 0, 0), datetime(2011, 1, 1, 0, 0)),
                         provider.temporal_coverage)

    @unittest.skipIf(not os.path.exists(SOURCE_DIR), 'test data not found: ' + SOURCE_DIR)
    def test_get_images(self):
        provider = CEmissionsProvider(CubeConfig(), dir=SOURCE_DIR)
        provider.prepare()
        images = provider.compute_variable_images(datetime(2001, 1, 1), datetime(2001, 1, 9))
        self.assertIsNotNone(images)
        self.assertTrue('c_emissions' in images)
        image = images['c_emissions']
        self.assertEqual((720, 1440), image.shape)

    @unittest.skipIf(not os.path.exists(SOURCE_DIR), 'test data not found: ' + SOURCE_DIR)
    def test_get_high_res_images(self):
        provider = CEmissionsProvider(CubeConfig(grid_width=4320, grid_height=2160, spatial_res=1 / 12), dir=SOURCE_DIR)
        provider.prepare()
        images = provider.compute_variable_images(datetime(2001, 1, 1), datetime(2001, 1, 9))
        self.assertIsNotNone(images)
        self.assertTrue('c_emissions' in images)
        image = images['c_emissions']
        self.assertEqual((2160, 4320), image.shape)
