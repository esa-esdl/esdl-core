import os
import unittest
from datetime import datetime

from cablab import CubeConfig
from cablab.providers.mpi_bgc import MPIBGCProvider
from cablab.util import Config

SOURCE_DIR = Config.instance().get_cube_source_path('MPI_BGC')


class MPIBGCTest(unittest.TestCase):
    @unittest.skipIf(not os.path.exists(SOURCE_DIR), 'test data not found: ' + SOURCE_DIR)
    def test_source_time_ranges(self):
        provider = MPIBGCProvider(CubeConfig(end_time=datetime(2001, 12, 31, 23, 0)), dir=SOURCE_DIR + "LE/", var="LE")
        provider.prepare()
        source_time_ranges = provider.source_time_ranges
        self.assertEqual(46, len(source_time_ranges))
        self.assertEqual((datetime(2001, 1, 9, 0, 0), datetime(2001, 1, 17, 0, 0),
                          os.path.join(SOURCE_DIR, 'LE/LE_2001.nc'), 1), source_time_ranges[1])
        self.assertEqual((datetime(2001, 12, 27, 0, 0), datetime(2002, 1, 4, 0, 0),
                          os.path.join(SOURCE_DIR, 'LE/LE_2001.nc'), 45), source_time_ranges[45])

    @unittest.skipIf(not os.path.exists(SOURCE_DIR), 'test data not found: ' + SOURCE_DIR)
    def test_temporal_coverage(self):
        provider = MPIBGCProvider(CubeConfig(end_time=datetime(2001, 12, 31, 23, 0)), dir=SOURCE_DIR + "H", var="H")
        provider.prepare()
        self.assertEqual((datetime(2001, 1, 1, 0, 0), datetime(2002, 1, 4, 0, 0)),
                         provider.temporal_coverage)

    @unittest.skipIf(not os.path.exists(SOURCE_DIR), 'test data not found: ' + SOURCE_DIR)
    def test_get_images(self):
        provider = MPIBGCProvider(CubeConfig(end_time=datetime(2001, 12, 31, 23, 0)), dir=SOURCE_DIR + "GPP",
                                  var="GPPall")
        provider.prepare()
        images = provider.compute_variable_images(datetime(2001, 1, 1), datetime(2001, 1, 9))
        self.assertIsNotNone(images)
        self.assertTrue('gross_primary_productivity' in images)
        image = images['gross_primary_productivity']
        self.assertEqual((720, 1440), image.shape)

    @unittest.skipIf(not os.path.exists(SOURCE_DIR), 'test data not found: ' + SOURCE_DIR)
    def test_get_high_res_images(self):
        provider = MPIBGCProvider(
            CubeConfig(grid_width=4320, grid_height=2160, spatial_res=1 / 12, end_time=datetime(2001, 12, 31, 23, 0)),
            dir=SOURCE_DIR + "NEE", var="NEE")
        provider.prepare()
        images = provider.compute_variable_images(datetime(2001, 1, 1), datetime(2001, 1, 9))
        self.assertIsNotNone(images)
        self.assertTrue('net_ecosystem_exchange' in images)
        image = images['net_ecosystem_exchange']
        self.assertEqual((2160, 4320), image.shape)
