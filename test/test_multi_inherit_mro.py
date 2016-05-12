"""
Test various MRO scenarios w.r.t. multiple inheritance.
Not a real test, but demonstrates some Python 3.x concepts.
"""

import unittest
from abc import abstractmethod, ABCMeta

TRACE = ''


# an abstract class A
class A(metaclass=ABCMeta):
    @abstractmethod
    def close(self):
        pass


# B is an A with a close() impl
class B(A):
    def close(self):
        global TRACE
        TRACE += 'B.close'


# A mixin class that provides a close() impl.
class M(object):
    def close(self):
        global TRACE
        TRACE += 'M.close'


# Not possible --> TypeError, wrong MRO
# class AB(A, B):
#    pass


class BA(B, A):
    pass


class AM(A, M):
    pass


class MA(M, A):
    pass


class BMA(B, M, A):
    pass


class MBA(M, B, A):
    pass


class MethodResolutionOrderTest(unittest.TestCase):
    def setUp(self):
        global TRACE
        TRACE = ''

    def _test_close(self, obj, expected):
        obj.close()
        self.assertEqual(expected, TRACE)

    def test_A(self):
        with self.assertRaises(TypeError):
            A()

    def test_B(self):
        self._test_close(B(), 'B.close')

    def test_BA(self):
        self._test_close(BA(), 'B.close')

    def test_AM(self):
        with self.assertRaises(TypeError):
            AM()

    def test_MA(self):
        self._test_close(MA(), 'M.close')

    def test_BMA(self):
        self._test_close(BMA(), 'B.close')

    def test_MBA(self):
        self._test_close(MBA(), 'M.close')


if __name__ == '__main__':
    unittest.main()
