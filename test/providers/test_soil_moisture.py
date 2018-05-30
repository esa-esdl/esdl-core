import os
import unittest
from datetime import datetime

from esdl import CubeConfig
from esdl.providers.soil_moisture import SoilMoistureProvider
from test.providers.provider_test_utils import ProviderTestBase
from esdl.util import Config

SOURCE_DIR = Config.instance().get_cube_source_path('ECV_sm')


class SoilMoistureProviderTest(ProviderTestBase):
    @unittest.skipIf(not os.path.exists(SOURCE_DIR), 'test data not found: ' + SOURCE_DIR)
    def test_source_time_ranges(self):
        provider = SoilMoistureProvider(CubeConfig(), dir=SOURCE_DIR)
        provider.prepare()
        source_time_ranges = provider.source_time_ranges
        self.assertEqual(12784, len(source_time_ranges))
        self.assert_source_time_ranges(source_time_ranges[0],
                                       datetime(1979, 1, 1, 0, 0, 0, 33),
                                       datetime(1979, 1, 2, 0, 0, 0, 33),
                                       self.get_source_dir_list(SOURCE_DIR) + [
                                           'SoilMoisture.ESACCI-L3S.1979.v2_1.nc.gz'],
                                       0)
        self.assert_source_time_ranges(source_time_ranges[6],
                                       datetime(1979, 1, 7, 0, 0, 0, 33),
                                       datetime(1979, 1, 8, 0, 0, 0, 33),
                                       self.get_source_dir_list(SOURCE_DIR) + [
                                           'SoilMoisture.ESACCI-L3S.1979.v2_1.nc.gz'],
                                       6)
        self.assert_source_time_ranges(source_time_ranges[12783],
                                       datetime(2013, 12, 31, 0, 0, 0, 33),
                                       datetime(2014, 1, 31, 0, 0, 0, 33),
                                       self.get_source_dir_list(SOURCE_DIR) + [
                                           'SoilMoisture.ESACCI-L3S.2013.v2_1.nc.gz'],
                                       364)

    @unittest.skipIf(not os.path.exists(SOURCE_DIR), 'test data not found: ' + SOURCE_DIR)
    def test_temporal_coverage(self):
        provider = SoilMoistureProvider(CubeConfig(), dir=SOURCE_DIR)
        provider.prepare()
        self.assertEqual((datetime(1979, 1, 1, 0, 0, 0, 33), datetime(2014, 1, 31, 0, 0, 0, 33)),
                         provider.temporal_coverage)

    @unittest.skipIf(not os.path.exists(SOURCE_DIR), 'test data not found: ' + SOURCE_DIR)
    def test_get_images(self):
        provider = SoilMoistureProvider(CubeConfig(), dir=SOURCE_DIR)
        provider.prepare()
        images = provider.compute_variable_images(datetime(1996, 1, 1), datetime(1996, 1, 9))
        self.assertIsNotNone(images)
        self.assertTrue('soil_moisture' in images)
        image = images['soil_moisture']
        self.assertEqual((720, 1440), image.shape)

    @unittest.skipIf(not os.path.exists(SOURCE_DIR), 'test data not found: ' + SOURCE_DIR)
    def test_get_high_res_images(self):
        provider = SoilMoistureProvider(CubeConfig(grid_width=4320, grid_height=2160, spatial_res=1 / 12),
                                        dir=SOURCE_DIR)
        provider.prepare()
        images = provider.compute_variable_images(datetime(1996, 1, 1), datetime(1996, 1, 9))
        self.assertIsNotNone(images)
        self.assertTrue('soil_moisture' in images)
        image = images['soil_moisture']
        self.assertEqual((2160, 4320), image.shape)
