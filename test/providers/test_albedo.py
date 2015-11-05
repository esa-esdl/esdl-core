import os
import unittest
from datetime import datetime

from cablab import CubeConfig
from cablab.providers.albedo import AlbedoProvider
from cablab.util import Config

# Only the first 3 files of each year (2000,2001,2002) were included due to their large size
SOURCE_DIR = Config.instance().get_cube_source_path('globalbedo')


class AlbedoProviderTest(unittest.TestCase):
    @unittest.skipIf(not os.path.exists(SOURCE_DIR), 'test data not found: ' + SOURCE_DIR)
    def test_source_time_ranges(self):
        provider = AlbedoProvider(CubeConfig(), SOURCE_DIR)
        provider.prepare()
        source_time_ranges = provider.get_source_time_ranges()
        self.assertEqual(9, len(source_time_ranges))
        self.assertEqual((datetime(2000, 1, 1, 0),
                          datetime(2000, 1, 9, 0),
                          os.path.join(SOURCE_DIR, '2000\\GlobAlbedo.2000001.mosaic.05.nc.gz'),
                          0), source_time_ranges[0])
        self.assertEqual((datetime(2000, 1, 9, 0),
                          datetime(2000, 1, 17, 0),
                          os.path.join(SOURCE_DIR, '2000\\GlobAlbedo.2000009.mosaic.05.nc.gz'),
                          0), source_time_ranges[1])
        self.assertEqual((datetime(2002, 12, 27, 0),
                          datetime(2003, 1, 4, 0),
                          os.path.join(SOURCE_DIR, '2002\\GlobAlbedo.2002361.mosaic.05.nc.gz'),
                          0), source_time_ranges[8])

    @unittest.skipIf(not os.path.exists(SOURCE_DIR), 'test data not found: ' + SOURCE_DIR)
    def test_temporal_coverage(self):
        provider = AlbedoProvider(CubeConfig(), SOURCE_DIR)
        provider.prepare()
        self.assertEqual((datetime(2000, 1, 1, 0, 0), datetime(2003, 1, 4, 0, 0)),
                         provider.get_temporal_coverage())

    @unittest.skipIf(not os.path.exists(SOURCE_DIR), 'test data not found: ' + SOURCE_DIR)
    def test_get_images(self):
        provider = AlbedoProvider(CubeConfig(), SOURCE_DIR)
        provider.prepare()
        images = provider.compute_variable_images(datetime(2000, 1, 10), datetime(2000, 1, 18))
        self.assertIsNotNone(images)
        self.assertTrue('Snow_Fraction' in images)
        image = images['Snow_Fraction']
        self.assertEqual((720, 1440), image.shape)
