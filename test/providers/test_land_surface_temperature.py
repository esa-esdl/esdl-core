import os
import unittest
from datetime import datetime

from cablab import CubeConfig
from cablab.providers.land_surface_temperature import LandSurfTemperatureProvider
from test.providers.provider_test_utils import ProviderTestBase
from cablab.util import Config

SOURCE_DIR = Config.instance().get_cube_source_path("globtemperature/ftp2.globtemperature.info/AATSR/L3/")


class LandSurfTemperatureProviderTest(ProviderTestBase):
    @unittest.skipIf(not os.path.exists(SOURCE_DIR), 'test data not found: ' + SOURCE_DIR)
    def test_source_time_ranges(self):
        provider = LandSurfTemperatureProvider(
            CubeConfig(start_time=datetime(2003, 1, 1, 0, 0), end_time=datetime(2003, 12, 31, 23, 0)), dir=SOURCE_DIR)
        provider.prepare()
        source_time_ranges = provider.source_time_ranges
        self.assertEqual(320, len(source_time_ranges))
        self.assert_source_time_ranges(source_time_ranges[0],
                                       datetime(2003, 1, 2, 0, 0),
                                       datetime(2003, 1, 3, 0, 0),
                                       self.get_source_dir_list(SOURCE_DIR) +
                                       ['GT_SSD-L3-AATSR_LST_3-20030102_H1.0V1.0-H36.0V18.0-CUOL-0.05X0.05-V1.0.nc'],
                                       0)
        self.assert_source_time_ranges(source_time_ranges[10],
                                       datetime(2003, 1, 13, 0, 0),
                                       datetime(2003, 1, 14, 0, 0),
                                       self.get_source_dir_list(SOURCE_DIR) +
                                       ['GT_SSD-L3-AATSR_LST_3-20030113_H1.0V1.0-H36.0V18.0-CUOL-0.05X0.05-V1.0.nc'],
                                       0)
        self.assert_source_time_ranges(source_time_ranges[20],
                                       datetime(2003, 1, 24, 0, 0),
                                       datetime(2003, 1, 25, 0, 0),
                                       self.get_source_dir_list(SOURCE_DIR) +
                                       ['GT_SSD-L3-AATSR_LST_3-20030124_H1.0V1.0-H36.0V18.0-CUOL-0.05X0.05-V1.0.nc'],
                                       0)

    @unittest.skipIf(not os.path.exists(SOURCE_DIR), 'test data not found: ' + SOURCE_DIR)
    def test_temporal_coverage(self):
        provider = LandSurfTemperatureProvider(
            CubeConfig(start_time=datetime(2003, 1, 1, 0, 0), end_time=datetime(2003, 12, 31, 23, 0)), dir=SOURCE_DIR)
        provider.prepare()
        self.assertEqual((datetime(2003, 1, 2, 0, 0), datetime(2004, 1, 1, 0, 0)),
                         provider.temporal_coverage)

    @unittest.skipIf(not os.path.exists(SOURCE_DIR), 'test data not found: ' + SOURCE_DIR)
    def test_get_images(self):
        provider = LandSurfTemperatureProvider(
            CubeConfig(start_time=datetime(2002, 6, 1, 0, 0), end_time=datetime(2002, 7, 1, 0, 0)), dir=SOURCE_DIR,
            resampling_order="space_first")
        provider.prepare()
        images = provider.compute_variable_images(datetime(2002, 6, 1), datetime(2002, 6, 10))
        self.assertIsNotNone(images)
        self.assertTrue('land_surface_temperature' in images)
        image = images['land_surface_temperature']
        self.assertEqual((720, 1440), image.shape)

    @unittest.skipIf(not os.path.exists(SOURCE_DIR), 'test data not found: ' + SOURCE_DIR)
    def test_get_high_res_images(self):
        provider = LandSurfTemperatureProvider(CubeConfig(grid_width=4320, grid_height=2160, spatial_res=1 / 12,
                                                          start_time=datetime(2002, 6, 1, 0, 0),
                                                          end_time=datetime(2002, 7, 1, 0, 0)),
                                               dir=SOURCE_DIR, resampling_order="space_first")
        provider.prepare()
        images = provider.compute_variable_images(datetime(2002, 6, 1), datetime(2002, 6, 10))
        self.assertIsNotNone(images)
        self.assertTrue('land_surface_temperature' in images)
        image = images['land_surface_temperature']
        self.assertEqual((2160, 4320), image.shape)
