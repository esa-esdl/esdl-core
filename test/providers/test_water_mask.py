import os
import unittest
from datetime import datetime
from cablab import CubeConfig
from cablab.providers.water_mask import WaterMaskProvider
from cablab.util import Config

SOURCE_DIR = Config.instance().get_cube_source_path('WaterBodies4.0')


class WaterMaskProviderTest(unittest.TestCase):
    @unittest.skipIf(not os.path.exists(SOURCE_DIR), 'test data not found: ' + SOURCE_DIR)
    def test_temporal_coverage(self):
        provider = WaterMaskProvider(CubeConfig(end_time=datetime(2003, 1, 1)), dir=SOURCE_DIR)
        provider.prepare()
        self.assertEqual((datetime(2001, 1, 1, 0, 0), datetime(2003, 1, 1, 0, 0)),
                         provider.temporal_coverage)

    @unittest.skipIf(not os.path.exists(SOURCE_DIR), 'test data not found: ' + SOURCE_DIR)
    def test_get_images(self):
        provider = WaterMaskProvider(CubeConfig(end_time=datetime(2003, 1, 1)), dir=SOURCE_DIR)
        provider.prepare()
        images = provider.compute_variable_images(datetime(2002, 7, 27), datetime(2002, 8, 4))

        self.assertIsNotNone(images)

        self.assertTrue('water_mask' in images)
        image = images['water_mask']
        self.assertEqual((720, 1440), image.shape)

    @unittest.skipIf(not os.path.exists(SOURCE_DIR), 'test data not found: ' + SOURCE_DIR)
    def test_get_high_res_images(self):
        provider = WaterMaskProvider(CubeConfig(grid_width=4320, grid_height=2160, spatial_res=1 / 12,
                                                  end_time=datetime(2003, 1, 1)), dir=SOURCE_DIR)
        provider.prepare()
        images = provider.compute_variable_images(datetime(2002, 7, 27), datetime(2002, 8, 4))

        self.assertIsNotNone(images)

        self.assertTrue('water_mask' in images)
        image = images['water_mask']
        self.assertEqual((2160, 4320), image.shape)

    @unittest.skipIf(not os.path.exists(SOURCE_DIR), 'test data not found: ' + SOURCE_DIR)
    def test_get_images_outside_time_range(self):
        provider = WaterMaskProvider(CubeConfig(end_time=datetime(2002, 1, 1)), dir=SOURCE_DIR)
        provider.prepare()
        images = provider.compute_variable_images(datetime(2016, 7, 27), datetime(2016, 8, 4))

        self.assertIsNotNone(images)

        self.assertTrue('water_mask' in images)
        image = images['water_mask']
        self.assertEqual((720, 1440), image.shape)
