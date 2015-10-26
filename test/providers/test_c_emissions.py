from unittest import TestCase
from datetime import datetime
import unittest
import os

from cablab import CubeConfig

from cablab.providers.c_emissions import CEmissionsProvider

EMISSIONS_SOURCE_PATH = 'W:\\Emissions'


class CEmissionsProviderTest(TestCase):
    @unittest.skipIf(not os.path.exists(EMISSIONS_SOURCE_PATH), 'test data not found: ' + EMISSIONS_SOURCE_PATH)
    def test_get_year_to_file_dict(self):
        file_dict = CEmissionsProvider._get_year_to_file_dict(EMISSIONS_SOURCE_PATH)
        self.assertEqual(18, len(file_dict))
        self.assertEqual(os.path.join(EMISSIONS_SOURCE_PATH, 'C_Emissions.1440.720.12.1996.nc.gz'), file_dict[1996])
        self.assertEqual(os.path.join(EMISSIONS_SOURCE_PATH, 'C_Emissions.1440.720.12.1997.nc.gz'), file_dict[1997])
        self.assertEqual(os.path.join(EMISSIONS_SOURCE_PATH, 'C_Emissions.1440.720.12.2001.nc.gz'), file_dict[2001])
        self.assertEqual(os.path.join(EMISSIONS_SOURCE_PATH, 'C_Emissions.1440.720.12.2011.nc.gz'), file_dict[2011])
        self.assertEqual(os.path.join(EMISSIONS_SOURCE_PATH, 'C_Emissions.1440.720.12.2012.nc.gz'), file_dict[2012])

    @unittest.skipIf(not os.path.exists(EMISSIONS_SOURCE_PATH), 'test data not found: ' + EMISSIONS_SOURCE_PATH)
    def test_get_temporal_coverage(self):
        provider = CEmissionsProvider(EMISSIONS_SOURCE_PATH)
        provider.prepare(CubeConfig())
        self.assertEqual((datetime(1996, 1, 1), datetime(2014, 1, 1)), provider.get_temporal_coverage())
        source_time_ranges = provider.get_source_time_ranges()
        self.assertEqual(18 * 12, len(source_time_ranges))
        self.assertEqual((datetime(1996, 1, 1), datetime(1996, 2, 1)), source_time_ranges[0])
        self.assertEqual((datetime(1996, 12, 1), datetime(1997, 1, 1)), source_time_ranges[11])
        self.assertEqual((datetime(2013, 11, 1), datetime(2013, 12, 1)), source_time_ranges[-2])
        self.assertEqual((datetime(2013, 12, 1), datetime(2014, 1, 1)), source_time_ranges[-1])

    @unittest.skipIf(not os.path.exists(EMISSIONS_SOURCE_PATH), 'test data not found: ' + EMISSIONS_SOURCE_PATH)
    def test_get_images(self):
        provider = CEmissionsProvider(EMISSIONS_SOURCE_PATH)
        provider.prepare(CubeConfig())
        self.assertEqual((datetime(1996, 1, 1), datetime(2014, 1, 1)), provider.get_temporal_coverage())
        images = provider.get_images(datetime(1996, 1, 1), datetime(1996, 1, 9))
        self.assertIsNotNone(images)
        self.assertTrue('C_Emissions' in images)
        image = images['C_Emissions']
        self.assertEqual((720, 1440), image.shape)
