import numpy as np
from skimage.measure import block_reduce
from numpy.testing import assert_array_equal
from unittest import TestCase
import gridtools.resampling as gtr


class AggregationTest(TestCase):
    def test_block_reduce_ndarray(self):
        test_array = np.arange(16).reshape((4, 4))
        assert_array_equal(test_array[0], [0, 1, 2, 3], verbose=True)
        assert_array_equal(test_array[1], [4, 5, 6, 7], verbose=True)
        assert_array_equal(test_array[2], [8, 9, 10, 11], verbose=True)
        assert_array_equal(test_array[3], [12, 13, 14, 15], verbose=True)

        mean_aggregated_array = block_reduce(test_array, (2, 2), func=np.mean)

        self.assertEqual((2, 2), mean_aggregated_array.shape)
        assert_array_equal(mean_aggregated_array[0], [(0 + 1 + 4 + 5) / 4, (2 + 3 + 6 + 7) / 4], verbose=True)
        assert_array_equal(mean_aggregated_array[1], [(8 + 9 + 12 + 13) / 4, (10 + 11 + 14 + 15) / 4], verbose=True)

    def test_resizer_ndarray(self):
        test_array = np.arange(16, dtype=np.float64).reshape((4, 4))
        assert_array_equal(test_array[0], [0, 1, 2, 3], verbose=True)
        assert_array_equal(test_array[1], [4, 5, 6, 7], verbose=True)
        assert_array_equal(test_array[2], [8, 9, 10, 11], verbose=True)
        assert_array_equal(test_array[3], [12, 13, 14, 15], verbose=True)

        mean_aggregated_array = gtr.resample2d(test_array, 2, 2)

        self.assertEqual((2, 2), mean_aggregated_array.shape)
        assert_array_equal(mean_aggregated_array[0], [(0 + 1 + 4 + 5) / 4, (2 + 3 + 6 + 7) / 4], verbose=True)
        assert_array_equal(mean_aggregated_array[1], [(8 + 9 + 12 + 13) / 4, (10 + 11 + 14 + 15) / 4], verbose=True)

    def test_block_reduce_mask_array(self):
        test_array = np.arange(16).reshape((4, 4))
        assert_array_equal(test_array[0], [0, 1, 2, 3], verbose=True)
        assert_array_equal(test_array[1], [4, 5, 6, 7], verbose=True)
        assert_array_equal(test_array[2], [8, 9, 10, 11], verbose=True)
        assert_array_equal(test_array[3], [12, 13, 14, 15], verbose=True)

        mask_array = np.full((4, 4), False, dtype=np.bool)
        mask_array[1:3, 1:3] = True
        assert_array_equal(mask_array[0], [False, False, False, False], verbose=True)
        assert_array_equal(mask_array[1], [False,  True,  True, False], verbose=True)
        assert_array_equal(mask_array[2], [False,  True,  True, False], verbose=True)
        assert_array_equal(mask_array[3], [False, False, False, False], verbose=True)

        masked_array = np.ma.array(test_array, mask=mask_array)
        self.assertTrue(np.ma.is_masked(masked_array))
        assert_array_equal(masked_array[0], [0, 1, 2, 3], verbose=True)
        assert_array_equal(masked_array[1], [4, np.nan, np.nan, 7], verbose=True)
        assert_array_equal(masked_array[2], [8, np.nan, np.nan, 11], verbose=True)
        assert_array_equal(masked_array[3], [12, 13, 14, 15], verbose=True)

        mean_aggregated_array = block_reduce(masked_array, (2, 2), func=np.mean)

        self.assertEqual((2, 2), mean_aggregated_array.shape)
        # The mask is ignored in the block_reduce function
        assert_array_equal(mean_aggregated_array[0], [(0 + 1 + 4 + 5) / 4, (2 + 3 + 6 + 7) / 4], verbose=True)
        assert_array_equal(mean_aggregated_array[1], [(8 + 9 + 12 + 13) / 4, (10 + 11 + 14 + 15) / 4], verbose=True)

        # What should have been if the mask is not ignored
        # assert_array_equal(mean_aggregated_array[0], [2.25, 4.75], verbose=True)
        # assert_array_equal(mean_aggregated_array[1], [10.25, 12.75], verbose=True)

    def test_rebin_mask_array(self):
        test_array = np.arange(16).reshape((4, 4))
        assert_array_equal(test_array[0], [0, 1, 2, 3], verbose=True)
        assert_array_equal(test_array[1], [4, 5, 6, 7], verbose=True)
        assert_array_equal(test_array[2], [8, 9, 10, 11], verbose=True)
        assert_array_equal(test_array[3], [12, 13, 14, 15], verbose=True)

        mask_array = np.full((4, 4), False, dtype=np.bool)
        mask_array[1:3, 1:3] = True
        assert_array_equal(mask_array[0], [False, False, False, False], verbose=True)
        assert_array_equal(mask_array[1], [False,  True,  True, False], verbose=True)
        assert_array_equal(mask_array[2], [False,  True,  True, False], verbose=True)
        assert_array_equal(mask_array[3], [False, False, False, False], verbose=True)

        masked_array = np.ma.array(test_array, mask=mask_array)
        self.assertTrue(np.ma.is_masked(masked_array))
        assert_array_equal(masked_array[0], [0, 1, 2, 3], verbose=True)
        assert_array_equal(masked_array[1], [4, np.nan, np.nan, 7], verbose=True)
        assert_array_equal(masked_array[2], [8, np.nan, np.nan, 11], verbose=True)
        assert_array_equal(masked_array[3], [12, 13, 14, 15], verbose=True)

        mean_aggregated_array = self._rebin(masked_array, (2, 2), func=np.ma.mean)
        self.assertEqual((2, 2), mean_aggregated_array.shape)
        assert_array_equal(mean_aggregated_array[0], [2.25, 4.75], verbose=True)
        assert_array_equal(mean_aggregated_array[1], [10.25, 12.75], verbose=True)

        max_aggregated_array = self._rebin(masked_array, (2, 2), func=np.ma.max)
        self.assertEqual((2, 2), max_aggregated_array.shape)
        assert_array_equal(max_aggregated_array[0], [4, 7], verbose=True)
        assert_array_equal(max_aggregated_array[1], [13, 15], verbose=True)

        min_aggregated_array = self._rebin(masked_array, (2, 2), func=np.ma.min)
        self.assertEqual((2, 2), min_aggregated_array.shape)
        assert_array_equal(min_aggregated_array[0], [0, 2], verbose=True)
        assert_array_equal(min_aggregated_array[1], [8, 11], verbose=True)

        median_aggregated_array = self._rebin(masked_array, (2, 2), func=np.ma.median)
        self.assertEqual((2, 2), median_aggregated_array.shape)
        assert_array_equal(median_aggregated_array[0], [2.25, 4.75], verbose=True)
        assert_array_equal(median_aggregated_array[1], [10.25, 12.75], verbose=True)

    def test_resizer_agg_with_mask_array(self):
        test_array = np.arange(16, dtype=np.float64).reshape((4, 4))
        assert_array_equal(test_array[0], [ 0,  1,  2,  3], verbose=True)
        assert_array_equal(test_array[1], [ 4,  5,  6,  7], verbose=True)
        assert_array_equal(test_array[2], [ 8,  9, 10, 11], verbose=True)
        assert_array_equal(test_array[3], [12, 13, 14, 15], verbose=True)

        mask_array = np.full((4, 4), False, dtype=np.bool)
        mask_array[1:3, 1:3] = True
        assert_array_equal(mask_array[0], [False, False, False, False], verbose=True)
        assert_array_equal(mask_array[1], [False,  True,  True, False], verbose=True)
        assert_array_equal(mask_array[2], [False,  True,  True, False], verbose=True)
        assert_array_equal(mask_array[3], [False, False, False, False], verbose=True)

        masked_array = np.ma.array(test_array, mask=mask_array)
        self.assertTrue(np.ma.is_masked(masked_array))
        assert_array_equal(masked_array[0], [0,      1,      2,  3], verbose=True)
        assert_array_equal(masked_array[1], [4, np.nan, np.nan,  7], verbose=True)
        assert_array_equal(masked_array[2], [8, np.nan, np.nan, 11], verbose=True)
        assert_array_equal(masked_array[3], [12,    13,     14, 15], verbose=True)

        mean_aggregated_array = gtr.resample2d(masked_array, 2, 2)
        self.assertEqual((2, 2), mean_aggregated_array.shape)
        assert_array_equal(mean_aggregated_array[0], [(0 + 1 + 4) / 3, (2 + 3 + 7) / 3], verbose=True)
        assert_array_equal(mean_aggregated_array[1], [(8 + 12 + 13) / 3, (11 + 14 + 15) / 3], verbose=True)

    def test_resizer_weighted_agg_with_mask_array(self):
        test_array = np.arange(20, dtype=np.float64).reshape((4, 5))
        assert_array_equal(test_array[0], [0, 1, 2, 3, 4], verbose=True)
        assert_array_equal(test_array[1], [5, 6, 7, 8, 9], verbose=True)
        assert_array_equal(test_array[2], [10, 11, 12, 13, 14], verbose=True)
        assert_array_equal(test_array[3], [15, 16, 17, 18, 19], verbose=True)

        mask_array = np.full((4, 5), False, dtype=np.bool)
        mask_array[1:3, 1:4] = True
        mask_array[1, 2] = False
        mask_array[2, 2] = False
        assert_array_equal(mask_array[0], [False, False, False, False, False], verbose=True)
        assert_array_equal(mask_array[1], [False,  True, False,  True, False], verbose=True)
        assert_array_equal(mask_array[2], [False,  True, False,  True, False], verbose=True)
        assert_array_equal(mask_array[3], [False, False, False, False, False], verbose=True)

        masked_array = np.ma.array(test_array, mask=mask_array)
        self.assertTrue(np.ma.is_masked(masked_array))
        assert_array_equal(masked_array[0], [0,       1,  2,      3,  4], verbose=True)
        assert_array_equal(masked_array[1], [5,  np.nan,  7, np.nan,  9], verbose=True)
        assert_array_equal(masked_array[2], [10, np.nan, 12, np.nan, 14], verbose=True)
        assert_array_equal(masked_array[3], [15,     16, 17,     18, 19], verbose=True)

        mean_aggregated_array = gtr.resample2d(masked_array, 2, 2)
        self.assertEqual((2, 2), mean_aggregated_array.shape)
        assert_array_equal(mean_aggregated_array[0], [(0 + 1 + (2 / 2) + 5 + (7 / 2)) / (3 + 2 * (1 / 2)),
                                                      ((2 / 2) + 3 + 4 + (7 / 2) + 9) / (2 * (1 / 2) + 3)],
                           verbose=True)
        assert_array_equal(mean_aggregated_array[1], [(10 + (12 / 2) + 15 + 16 + (17 / 2)) / (3 + 2 * (1 / 2)),
                                                      ((12 / 2) + 14 + (17 / 2) + 18 + 19) / (2 * (1 / 2) + 3)],
                           verbose=True)

    def _rebin(self, a, shape, func=np.ma.mean):
        sh = shape[0], a.shape[0] // shape[0], shape[1], a.shape[1] // shape[1]
        return func(func(a.reshape(sh), -1), 1)
