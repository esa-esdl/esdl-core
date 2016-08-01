import os
import unittest
from datetime import datetime
from cablab import CubeConfig
from cablab.providers.aerosols import AerosolsProvider
from cablab.util import Config

SOURCE_DIR = Config.instance().get_cube_source_path('CCI-Aerosols/AATSR_SU_v4.1/L3_DAILY')


class AerosolsProviderTest(unittest.TestCase):
    @unittest.skipIf(not os.path.exists(SOURCE_DIR), 'test data not found: ' + SOURCE_DIR)
    def test_source_time_ranges(self):
        provider = AerosolsProvider(CubeConfig(end_time=datetime(2003, 1, 1)), dir=SOURCE_DIR)
        provider.prepare()
        source_time_ranges = provider.source_time_ranges
        self.assertEqual(97, len(source_time_ranges))
        self.assert_source_time_ranges(source_time_ranges[0],
                                       datetime(2002, 7, 24, 0, 0),
                                       datetime(2002, 7, 25, 0, 0),
                                       self.get_source_dir_list() +
                                       ['2002', '20020724-ESACCI-L3C_AEROSOL-AOD-AATSR_ENVISAT-SU_DAILY-fv4.1.nc'],
                                       0)
        self.assert_source_time_ranges(source_time_ranges[6],
                                       datetime(2002, 8, 6, 0, 0),
                                       datetime(2002, 8, 7, 0, 0),
                                       self.get_source_dir_list() +
                                       ['2002', '20020806-ESACCI-L3C_AEROSOL-AOD-AATSR_ENVISAT-SU_DAILY-fv4.1.nc'],
                                       0)
        self.assert_source_time_ranges(source_time_ranges[96],
                                       datetime(2003, 1, 1, 0, 0),
                                       datetime(2003, 1, 2, 0, 0),
                                       self.get_source_dir_list() +
                                       ['2003', '20030101-ESACCI-L3C_AEROSOL-AOD-AATSR_ENVISAT-SU_DAILY-fv4.1.nc'],
                                       0)

    def get_source_dir_list(self):
        return SOURCE_DIR.replace('\\', '/').split('/')

    def assert_source_time_ranges(self, source_time_ranges, expected_start_date,
                                  expected_end_date, expected_paths, expected_index):
        self.assertEqual(expected_start_date, source_time_ranges[0])
        self.assertEqual(expected_end_date, source_time_ranges[1])
        for path in expected_paths:
            self.assertIn(path, source_time_ranges[2].replace('\\', '/'))
        self.assertEqual(expected_index, source_time_ranges[3])

    @unittest.skipIf(not os.path.exists(SOURCE_DIR), 'test data not found: ' + SOURCE_DIR)
    def test_temporal_coverage(self):
        provider = AerosolsProvider(CubeConfig(end_time=datetime(2003, 1, 1)), dir=SOURCE_DIR)
        provider.prepare()
        self.assertEqual((datetime(2002, 7, 24, 0, 0), datetime(2003, 1, 2, 0, 0)),
                         provider.temporal_coverage)

    @unittest.skipIf(not os.path.exists(SOURCE_DIR), 'test data not found: ' + SOURCE_DIR)
    def test_get_images(self):
        provider = AerosolsProvider(CubeConfig(end_time=datetime(2003, 1, 1)), dir=SOURCE_DIR)
        provider.prepare()
        images = provider.compute_variable_images(datetime(2002, 7, 27), datetime(2002, 8, 4))

        self.assertIsNotNone(images)

        self.assertTrue('aerosol_optical_thickness_1610' in images)
        image = images['aerosol_optical_thickness_1610']
        self.assertEqual((720, 1440), image.shape)

        self.assertTrue('aerosol_optical_thickness_550' in images)
        image = images['aerosol_optical_thickness_550']
        self.assertEqual((720, 1440), image.shape)

        self.assertTrue('aerosol_optical_thickness_555' in images)
        image = images['aerosol_optical_thickness_555']
        self.assertEqual((720, 1440), image.shape)

        self.assertTrue('aerosol_optical_thickness_659' in images)
        image = images['aerosol_optical_thickness_659']
        self.assertEqual((720, 1440), image.shape)

        self.assertTrue('aerosol_optical_thickness_865' in images)
        image = images['aerosol_optical_thickness_865']
        self.assertEqual((720, 1440), image.shape)

    @unittest.skipIf(not os.path.exists(SOURCE_DIR), 'test data not found: ' + SOURCE_DIR)
    def test_get_high_res_images(self):
        provider = AerosolsProvider(CubeConfig(grid_width=4320, grid_height=2160, spatial_res=1 / 12,
                                               end_time=datetime(2003, 1, 1)), dir=SOURCE_DIR)
        provider.prepare()
        images = provider.compute_variable_images(datetime(2002, 7, 27), datetime(2002, 8, 4))

        self.assertIsNotNone(images)

        self.assertTrue('aerosol_optical_thickness_1610' in images)
        image = images['aerosol_optical_thickness_1610']
        self.assertEqual((2160, 4320), image.shape)

        self.assertTrue('aerosol_optical_thickness_550' in images)
        image = images['aerosol_optical_thickness_550']
        self.assertEqual((2160, 4320), image.shape)

        self.assertTrue('aerosol_optical_thickness_555' in images)
        image = images['aerosol_optical_thickness_555']
        self.assertEqual((2160, 4320), image.shape)

        self.assertTrue('aerosol_optical_thickness_659' in images)
        image = images['aerosol_optical_thickness_659']
        self.assertEqual((2160, 4320), image.shape)

        self.assertTrue('aerosol_optical_thickness_865' in images)
        image = images['aerosol_optical_thickness_865']
        self.assertEqual((2160, 4320), image.shape)
