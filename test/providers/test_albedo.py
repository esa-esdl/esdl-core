import os
import unittest
from datetime import datetime

from cablab import CubeConfig
from cablab.providers.albedo import AlbedoProvider
from cablab.util import Config

SOURCE_DIR = Config.instance().get_cube_source_path('globalbedo')


class AlbedoProviderTest(unittest.TestCase):
    @unittest.skipIf(not os.path.exists(SOURCE_DIR), 'test data not found: ' + SOURCE_DIR)
    def test_source_time_ranges(self):
        provider = AlbedoProvider(CubeConfig(end_time=datetime(2001, 2, 1)), SOURCE_DIR)
        provider.prepare()
        source_time_ranges = provider.get_source_time_ranges()
        self.assertEqual(4, len(source_time_ranges))
        self.assertEqual((datetime(2001, 1, 1, 0),
                          datetime(2001, 1, 9, 0),
                          os.path.join(SOURCE_DIR, '2001\\GlobAlbedo.2001001.mosaic.05.nc.gz'),
                          0), source_time_ranges[0])
        self.assertEqual((datetime(2001, 1, 9, 0),
                          datetime(2001, 1, 17, 0),
                          os.path.join(SOURCE_DIR, '2001\\GlobAlbedo.2001009.mosaic.05.nc.gz'),
                          0), source_time_ranges[1])
        self.assertEqual((datetime(2001, 1, 25, 0),
                          datetime(2001, 2, 2, 0),
                          os.path.join(SOURCE_DIR, '2001\\GlobAlbedo.2001025.mosaic.05.nc.gz'),
                          0), source_time_ranges[3])

    @unittest.skipIf(not os.path.exists(SOURCE_DIR), 'test data not found: ' + SOURCE_DIR)
    def test_temporal_coverage(self):
        provider = AlbedoProvider(CubeConfig(end_time=datetime(2001, 2, 1)), SOURCE_DIR)
        provider.prepare()
        self.assertEqual((datetime(2001, 1, 1, 0, 0), datetime(2001, 2, 2, 0, 0)),
                         provider.get_temporal_coverage())

    @unittest.skipIf(not os.path.exists(SOURCE_DIR), 'test data not found: ' + SOURCE_DIR)
    def test_get_images(self):
        provider = AlbedoProvider(CubeConfig(end_time=datetime(2001, 2, 1)), SOURCE_DIR)
        provider.prepare()
        images = provider.compute_variable_images(datetime(2001, 1, 1), datetime(2001, 1, 9))
        self.assertIsNotNone(images)
        self.assertTrue('Snow_Fraction' in images)
        image = images['Snow_Fraction']
        self.assertEqual((720, 1440), image.shape)
