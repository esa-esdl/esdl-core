import os
import unittest
from datetime import datetime

from cablab import CubeConfig
from cablab.providers.albedo import AlbedoProvider
from cablab.util import Config

SOURCE_DIR = Config.instance().get_cube_source_path('globalbedo_CF_compliant\\05deg\\8daily')


class AlbedoProviderTest(unittest.TestCase):
    @unittest.skipIf(not os.path.exists(SOURCE_DIR), 'test data not found: ' + SOURCE_DIR)
    def test_source_time_ranges(self):
        provider = AlbedoProvider(CubeConfig(), dir=SOURCE_DIR)
        provider.prepare()
        source_time_ranges = provider.source_time_ranges
        self.assertEqual(461, len(source_time_ranges))
        self.assertEqual((datetime(2001, 1, 1, 0),
                          datetime(2001, 1, 9, 0),
                          os.path.join(SOURCE_DIR, 'GlobAlbedo.merge.albedo.05.2001001.nc'),
                          0), source_time_ranges[0])
        self.assertEqual((datetime(2001, 1, 9, 0),
                          datetime(2001, 1, 17, 0),
                          os.path.join(SOURCE_DIR, 'GlobAlbedo.merge.albedo.05.2001009.nc'),
                          0), source_time_ranges[1])
        self.assertEqual((datetime(2001, 3, 22, 0),
                          datetime(2001, 3, 30, 0),
                          os.path.join(SOURCE_DIR, 'GlobAlbedo.merge.albedo.05.2001081.nc'),
                          0), source_time_ranges[10])

    @unittest.skipIf(not os.path.exists(SOURCE_DIR), 'test data not found: ' + SOURCE_DIR)
    def test_temporal_coverage(self):
        provider = AlbedoProvider(CubeConfig(), dir=SOURCE_DIR)
        provider.prepare()
        self.assertEqual((datetime(2001, 1, 1, 0, 0), datetime(2011, 1, 9, 0, 0)),
                         provider.temporal_coverage)

    @unittest.skipIf(not os.path.exists(SOURCE_DIR), 'test data not found: ' + SOURCE_DIR)
    def test_get_images(self):
        provider = AlbedoProvider(CubeConfig(), dir=SOURCE_DIR)
        provider.prepare()
        images = provider.compute_variable_images(datetime(2001, 1, 1), datetime(2001, 1, 9))
        self.assertIsNotNone(images)

        self.assertTrue('white_sky_albedo' in images)
        image = images['white_sky_albedo']
        self.assertEqual((720, 1440), image.shape)

        self.assertTrue('black_sky_albedo' in images)
        image = images['black_sky_albedo']
        self.assertEqual((720, 1440), image.shape)

    @unittest.skipIf(not os.path.exists(SOURCE_DIR), 'test data not found: ' + SOURCE_DIR)
    def test_get_high_res_images(self):
        provider = AlbedoProvider(CubeConfig(grid_width=4320, grid_height=2160, spatial_res=1 / 12), dir=SOURCE_DIR)
        provider.prepare()
        images = provider.compute_variable_images(datetime(2001, 1, 1), datetime(2001, 1, 9))
        self.assertIsNotNone(images)

        self.assertTrue('white_sky_albedo' in images)
        image = images['white_sky_albedo']
        self.assertEqual((2160, 4320), image.shape)

        self.assertTrue('black_sky_albedo' in images)
        image = images['black_sky_albedo']
        self.assertEqual((2160, 4320), image.shape)
