import os
import unittest
from datetime import datetime

from cablab import CubeConfig
from cablab.providers.precip import PrecipProvider
from cablab.util import Config

SOURCE_DIR = Config.instance().get_cube_source_path('CPC_precip')


class PrecipProviderTest(unittest.TestCase):
    @unittest.skipIf(not os.path.exists(SOURCE_DIR), 'test data not found: ' + SOURCE_DIR)
    def test_source_time_ranges(self):
        provider = PrecipProvider(CubeConfig(), SOURCE_DIR)
        provider.prepare()
        source_time_ranges = provider.get_source_time_ranges()
        self.assertEqual(13149, len(source_time_ranges))
        self.assertEqual((datetime(1979, 1, 1, 0, 0, 0, 33),
                          datetime(1979, 1, 2, 0, 0, 0, 33),
                          os.path.join(SOURCE_DIR, 'Precip.V1.720.360.1979.nc.gz'),
                          0), source_time_ranges[0])
        self.assertEqual((datetime(1979, 1, 7, 0, 0, 0, 33),
                          datetime(1979, 1, 8, 0, 0, 0, 33),
                          os.path.join(SOURCE_DIR, 'Precip.V1.720.360.1979.nc.gz'),
                          6), source_time_ranges[6])
        self.assertEqual((datetime(2014, 12, 31, 0, 0, 0, 33),
                          datetime(2015, 1, 1, 0, 0, 0, 33),
                          os.path.join(SOURCE_DIR, 'Precip.RT.720.360.2014.nc.gz'),
                          364), source_time_ranges[13148])

    @unittest.skipIf(not os.path.exists(SOURCE_DIR), 'test data not found: ' + SOURCE_DIR)
    def test_temporal_coverage(self):
        provider = PrecipProvider(CubeConfig(), SOURCE_DIR)
        provider.prepare()
        self.assertEqual((datetime(1979, 1, 1, 0, 0, 0, 33), datetime(2015, 1, 1, 0, 0, 0, 33)),
                         provider.get_temporal_coverage())

    @unittest.skipIf(not os.path.exists(SOURCE_DIR), 'test data not found: ' + SOURCE_DIR)
    def test_get_images(self):
        provider = PrecipProvider(CubeConfig(), SOURCE_DIR)
        provider.prepare()
        images = provider.compute_variable_images(datetime(1996, 1, 1), datetime(1996, 1, 9))
        self.assertIsNotNone(images)
        self.assertTrue('Precip' in images)
        image = images['Precip']
        self.assertEqual((720, 1440), image.shape)

    @unittest.skipIf(not os.path.exists(SOURCE_DIR), 'test data not found: ' + SOURCE_DIR)
    def test_get_high_res_images(self):
        provider = PrecipProvider(CubeConfig(grid_width=4320, grid_height=2160, spatial_res=1/12), SOURCE_DIR)
        provider.prepare()
        images = provider.compute_variable_images(datetime(1996, 1, 1), datetime(1996, 1, 9))
        self.assertIsNotNone(images)
        self.assertTrue('Precip' in images)
        image = images['Precip']
        self.assertEqual((2160, 4320), image.shape)
