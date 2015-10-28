from datetime import datetime
import unittest
import os

from cablab import CubeConfig
from cablab.providers.c_emissions import CEmissionsProvider

SOURCE_DIR = 'W:\\Emissions'


class CEmissionsProviderTest(unittest.TestCase):
    @unittest.skipIf(not os.path.exists(SOURCE_DIR), 'test data not found: ' + SOURCE_DIR)
    def test_source_time_ranges(self):
        provider = CEmissionsProvider(CubeConfig(), SOURCE_DIR)
        provider.prepare()
        source_time_ranges = provider.get_source_time_ranges()
        self.assertEqual(216, len(source_time_ranges))
        self.assertEqual((datetime(1996, 1, 1, 0, 0, 0, 33),
                          datetime(1996, 2, 1, 0, 0, 0, 33),
                          os.path.join(SOURCE_DIR, 'C_Emissions.1440.720.12.1996.nc.gz'),
                          0), source_time_ranges[0])
        self.assertEqual((datetime(1996, 7, 1, 0, 0, 0, 33),
                          datetime(1996, 8, 1, 0, 0, 0, 33),
                          os.path.join(SOURCE_DIR, 'C_Emissions.1440.720.12.1996.nc.gz'),
                          6), source_time_ranges[6])
        self.assertEqual((datetime(2013, 12, 1, 0, 0, 0, 33),
                          datetime(2014, 1, 1, 0, 0, 0, 33),
                          os.path.join(SOURCE_DIR, 'C_Emissions.1440.720.12.2013.nc.gz'),
                          11), source_time_ranges[215])

    @unittest.skipIf(not os.path.exists(SOURCE_DIR), 'test data not found: ' + SOURCE_DIR)
    def test_temporal_coverage(self):
        provider = CEmissionsProvider(CubeConfig(), SOURCE_DIR)
        provider.prepare()
        self.assertEqual((datetime(1996, 1, 1, 0, 0, 0, 33), datetime(2014, 1, 1, 0, 0, 0, 33)),
                         provider.get_temporal_coverage())

    @unittest.skipIf(not os.path.exists(SOURCE_DIR), 'test data not found: ' + SOURCE_DIR)
    def test_get_images(self):
        provider = CEmissionsProvider(CubeConfig(), SOURCE_DIR)
        provider.prepare()
        images = provider.compute_variable_images(datetime(1996, 1, 1), datetime(1996, 1, 9))
        self.assertIsNotNone(images)
        self.assertTrue('C_Emissions' in images)
        image = images['C_Emissions']
        self.assertEqual((720, 1440), image.shape)
