import os
import unittest
from datetime import datetime

from esdl import CubeConfig
from esdl.providers.ozone import OzoneProvider
from test.providers.provider_test_utils import ProviderTestBase
from esdl.util import Config

SOURCE_DIR = Config.instance().get_cube_source_path('Ozone-CCI/Total_Columns\\L3\\MERGED')


class OzoneProviderTest(ProviderTestBase):
    @unittest.skipIf(not os.path.exists(SOURCE_DIR), 'test data not found: ' + SOURCE_DIR)
    def test_source_time_ranges(self):
        provider = OzoneProvider(CubeConfig(), dir=SOURCE_DIR)
        provider.prepare()
        source_time_ranges = provider.source_time_ranges
        self.assertEqual(185, len(source_time_ranges))
        self.assert_source_time_ranges(source_time_ranges[0],
                                       datetime(1996, 3, 10, 0, 0),
                                       datetime(1996, 3, 31, 0, 0),
                                       self.get_source_dir_list(SOURCE_DIR) + [
                                           'ESACCI-OZONE-L3S-TC-MERGED-DLR_1M-19960310-fv0100.nc'],
                                       None)
        self.assert_source_time_ranges(source_time_ranges[6],
                                       datetime(1996, 9, 1, 0, 0),
                                       datetime(1996, 9, 30, 0, 0),
                                       self.get_source_dir_list(SOURCE_DIR) + [
                                           'ESACCI-OZONE-L3S-TC-MERGED-DLR_1M-19960901-fv0100.nc'],
                                       None)
        self.assert_source_time_ranges(source_time_ranges[184],
                                       datetime(2011, 6, 1, 0, 0),
                                       datetime(2011, 6, 30, 0, 0),
                                       self.get_source_dir_list(SOURCE_DIR) + [
                                           'ESACCI-OZONE-L3S-TC-MERGED-DLR_1M-20110601-fv0100.nc'],
                                       None)

    @unittest.skipIf(not os.path.exists(SOURCE_DIR), 'test data not found: ' + SOURCE_DIR)
    def test_temporal_coverage(self):
        provider = OzoneProvider(CubeConfig(), dir=SOURCE_DIR)
        provider.prepare()
        self.assertEqual((datetime(1996, 3, 10, 0, 0), datetime(2011, 6, 30, 0, 0)),
                         provider.temporal_coverage)

    @unittest.skipIf(not os.path.exists(SOURCE_DIR), 'test data not found: ' + SOURCE_DIR)
    def test_get_images(self):
        provider = OzoneProvider(CubeConfig(), dir=SOURCE_DIR)
        provider.prepare()
        images = provider.compute_variable_images(datetime(1996, 6, 1), datetime(1996, 6, 9))
        self.assertIsNotNone(images)
        self.assertTrue('ozone' in images)
        image = images['ozone']
        self.assertEqual((720, 1440), image.shape)

    @unittest.skipIf(not os.path.exists(SOURCE_DIR), 'test data not found: ' + SOURCE_DIR)
    def test_get_high_res_images(self):
        provider = OzoneProvider(CubeConfig(grid_width=4320, grid_height=2160, spatial_res=1 / 12), dir=SOURCE_DIR)
        provider.prepare()
        images = provider.compute_variable_images(datetime(1996, 6, 1), datetime(1996, 6, 9))
        self.assertIsNotNone(images)
        self.assertTrue('ozone' in images)
        image = images['ozone']
        self.assertEqual((2160, 4320), image.shape)
