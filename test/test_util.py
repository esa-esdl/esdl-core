import unittest

import numpy

from cablab.util import aggregate_images
from cablab.util import temporal_weight
from cablab.util import resolve_temporal_range_index

from datetime import datetime


class UtilTest(unittest.TestCase):
    def test_temporal_weight(self):
        self.assertEqual(temporal_weight(1, 3, 4, 8), 0.0)
        self.assertEqual(temporal_weight(1, 4, 4, 8), 0.0)
        self.assertEqual(temporal_weight(1, 5, 4, 8), 0.25)
        self.assertEqual(temporal_weight(1, 6, 4, 8), 0.5)
        self.assertEqual(temporal_weight(1, 7, 4, 8), 0.75)
        self.assertEqual(temporal_weight(1, 8, 4, 8), 1.0)
        self.assertEqual(temporal_weight(1, 9, 4, 8), 1.0)
        self.assertEqual(temporal_weight(4, 8, 4, 8), 1.0)
        self.assertEqual(temporal_weight(5, 8, 4, 8), 1.0)
        self.assertEqual(temporal_weight(5, 6, 4, 8), 1.0)
        self.assertEqual(temporal_weight(5, 9, 4, 8), 0.75)
        self.assertEqual(temporal_weight(6, 9, 4, 8), 0.5)
        self.assertEqual(temporal_weight(7, 9, 4, 8), 0.25)
        self.assertEqual(temporal_weight(9, 10, 4, 8), 0.0)

    def test_aggregate_time_series(self):
        im1 = numpy.ma.masked_array([[1.1, 2.1], [3.1, 4.1]], mask=[[1, 0], [1, 0]])
        im2 = numpy.ma.masked_array([[2.2, 3.2], [4.2, 5.2]], mask=[[0, 1], [1, 0]])
        im3 = numpy.ma.masked_array([[3.3, 4.3], [5.3, 6.3]], mask=[[1, 0], [1, 0]])

        im = aggregate_images((im1, im2, im3))

        self.assertEqual(im.shape, (2, 2))
        self.assertTrue(numpy.ma.is_masked(im))

        self.assertAlmostEqual(im[0][0], 2.2, places=3)
        self.assertAlmostEqual(im[0][1], (2.1 + 4.3) / 2, places=3)
        self.assertIs(im[1][0], numpy.ma.masked)
        self.assertAlmostEqual(im[1][1], (4.1 + 5.2 + 6.3) / 3, places=3)

        im = aggregate_images((im1, im2, im3), weights=(0.5, 1.0, 0.25))

        self.assertEqual(im.shape, (2, 2))
        self.assertTrue(numpy.ma.is_masked(im))

        self.assertAlmostEqual(im[0][0], 2.2, places=3)
        self.assertAlmostEqual(im[0][1], (0.5 * 2.1 + 0.25 * 4.3) / 2, places=4)
        self.assertIs(im[1][0], numpy.ma.masked)
        self.assertAlmostEqual(im[1][1], (0.5 * 4.1 + 1.0 * 5.2 + 0.25 * 6.3) / 3, places=3)

    def test_resolve_temporal_range_index(self):
        time1_index, time2_index = resolve_temporal_range_index(2001, 2011, 8,
                                                                datetime(2001, 1, 1),
                                                                datetime(2001, 12, 31))
        self.assertEqual(time1_index, 0)
        self.assertEqual(time2_index, 45)

        time1_index, time2_index = resolve_temporal_range_index(2001, 2011, 8,
                                                                datetime(2002, 1, 1),
                                                                datetime(2011, 12, 31))
        self.assertEqual(time1_index, 46)
        self.assertEqual(time2_index, 505)

        time1_index, time2_index = resolve_temporal_range_index(2001, 2011, 8,
                                                                datetime(2002, 6, 1),
                                                                datetime(2005, 6, 1))
        self.assertEqual(time1_index, 64)
        self.assertEqual(time2_index, 202)

        time1_index, time2_index = resolve_temporal_range_index(2001, 2011, 8,
                                                                datetime(2000, 1, 1),
                                                                datetime(2005, 12, 31))
        self.assertEqual(time1_index, 0)
        self.assertEqual(time2_index, 229)

        time1_index, time2_index = resolve_temporal_range_index(2001, 2011, 8,
                                                                datetime(2000, 1, 1),
                                                                datetime(2020, 12, 31))
        self.assertEqual(time1_index, 0)
        self.assertEqual(time2_index, 505)
