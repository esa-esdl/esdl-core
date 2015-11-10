import unittest

import numpy

from cablab.util import aggregate_images
from cablab.util import temporal_weight


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
