import unittest

import numpy as np

from cablab.resize import resize

F = np.nan


def test_resize(sw, sh, source, dw, dh, dest_desired):
    actual = resize(sw, sh, np.array(source), dw, dh)
    np.testing.assert_almost_equal(actual, np.array(dest_desired), err_msg='Cython resizer impl.')


class ResizerTest(unittest.TestCase):
    def test_no_op(self):
        test_resize(2, 2, [[1., 2.], [3., 4.]],
                    2, 2, [[1., 2.], [3., 4.]])

    def test_interpolation(self):
        test_resize(3, 1, [[1., 2., 3.]],
                    5, 1, [[1, 1.5, 2, 2.5, 3]]),

        test_resize(3, 1, [[1., 2., 3.]],
                    9, 1, [[1, 1.25, 1.5, 1.75, 2, 2.25, 2.5, 2.75, 3]])

        test_resize(4, 1, [[1., 2., 3., 4.]],
                    6, 1, [[1, 1.6, 2.2, 2.8, 3.4, 4]]),

        test_resize(2, 2, [[1., 2.],
                           [3., 4.]],
                    4, 4, [[3. / 3, 4. / 3, 5. / 3, 6. / 3],
                           [5. / 3, 6. / 3, 7. / 3, 8. / 3],
                           [7. / 3, 8. / 3, 9. / 3, 10. / 3],
                           [9. / 3, 10. / 3, 11. / 3, 12. / 3]]),

        test_resize(2, 2, [[1., 2.],
                           [3., 4.]],
                    4, 4, [[3. / 3, 4. / 3, 5. / 3, 6. / 3],
                           [5. / 3, 6. / 3, 7. / 3, 8. / 3],
                           [7. / 3, 8. / 3, 9. / 3, 10. / 3],
                           [9. / 3, 10. / 3, 11. / 3, 12. / 3]])

    def test_aggregation(self):
        test_resize(3, 3, [[0.6, 0.2, 3.4],
                           [1.4, 1.6, 1.0],
                           [4.0, 2.8, 3.0]],
                    2, 2, [[(0.6 + 0.5 * 0.2 + 0.5 * 1.4 + 0.25 * 1.6) / (1.0 + 0.5 + 0.5 + 0.25),
                            (3.4 + 0.5 * 0.2 + 0.5 * 1.0 + 0.25 * 1.6) / (1.0 + 0.5 + 0.5 + 0.25)],
                           [(4.0 + 0.5 * 1.4 + 0.5 * 2.8 + 0.25 * 1.6) / (1.0 + 0.5 + 0.5 + 0.25),
                            (3.0 + 0.5 * 1.0 + 0.5 * 2.8 + 0.25 * 1.6) / (1.0 + 0.5 + 0.5 + 0.25)]])

        test_resize(4, 4, [[0.9, 0.5, 3.0, 4.0],
                           [1.1, 1.5, 1.0, 2.0],
                           [4.0, 2.1, 3.0, 5.0],
                           [3.0, 4.9, 3.0, 1.0]],
                    2, 2, [[1.0, 2.5],
                           [3.5, 3.0]])