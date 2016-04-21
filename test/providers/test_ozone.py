import os
import unittest
from datetime import datetime

from cablab import CubeConfig
from cablab.providers.ozone import OzoneProvider
from cablab.util import Config

SOURCE_DIR = Config.instance().get_cube_source_path('Ozone-CCI\\Total_Columns\\L3\\MERGED')


class OzoneProviderTest(unittest.TestCase):
    @unittest.skipIf(not os.path.exists(SOURCE_DIR), 'test data not found: ' + SOURCE_DIR)
    def test_source_time_ranges(self):
        provider = OzoneProvider(CubeConfig(), SOURCE_DIR)
        provider.prepare()
        source_time_ranges = provider.get_source_time_ranges()
        self.assertEqual(185, len(source_time_ranges))
        self.assertEqual((datetime(1996, 3, 10, 0, 0),
                          datetime(1996, 3, 31, 0, 0),
                          os.path.join(SOURCE_DIR, 'ESACCI-OZONE-L3S-TC-MERGED-DLR_1M-19960310-fv0100.nc'))
                         , source_time_ranges[0])
        self.assertEqual((datetime(1996, 9, 1, 0, 0),
                          datetime(1996, 9, 30, 0, 0),
                          os.path.join(SOURCE_DIR, 'ESACCI-OZONE-L3S-TC-MERGED-DLR_1M-19960901-fv0100.nc'))
                         , source_time_ranges[6])
        self.assertEqual((datetime(2011, 6, 1, 0, 0),
                          datetime(2011, 6, 30, 0, 0),
                          os.path.join(SOURCE_DIR, 'ESACCI-OZONE-L3S-TC-MERGED-DLR_1M-20110601-fv0100.nc'))
                         , source_time_ranges[184])

    @unittest.skipIf(not os.path.exists(SOURCE_DIR), 'test data not found: ' + SOURCE_DIR)
    def test_temporal_coverage(self):
        provider = OzoneProvider(CubeConfig(), SOURCE_DIR)
        provider.prepare()
        self.assertEqual((datetime(1996, 3, 10, 0, 0), datetime(2011, 6, 30, 0, 0)),
                         provider.get_temporal_coverage())

    @unittest.skipIf(not os.path.exists(SOURCE_DIR), 'test data not found: ' + SOURCE_DIR)
    def test_get_images(self):
        provider = OzoneProvider(CubeConfig(), SOURCE_DIR)
        provider.prepare()
        images = provider.compute_variable_images(datetime(1996, 6, 1), datetime(1996, 6, 9))
        self.assertIsNotNone(images)
        self.assertTrue('Ozone' in images)
        image = images['Ozone']
        self.assertEqual((720, 1440), image.shape)

    @unittest.skipIf(not os.path.exists(SOURCE_DIR), 'test data not found: ' + SOURCE_DIR)
    def test_get_high_res_images(self):
        provider = OzoneProvider(CubeConfig(grid_width=4320, grid_height=2160, spatial_res=1 / 12), SOURCE_DIR)
        provider.prepare()
        images = provider.compute_variable_images(datetime(1996, 6, 1), datetime(1996, 6, 9))
        self.assertIsNotNone(images)
        self.assertTrue('Ozone' in images)
        image = images['Ozone']
        self.assertEqual((2160, 4320), image.shape)
