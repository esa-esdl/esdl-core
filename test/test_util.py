from datetime import datetime
import unittest

import netCDF4
import numpy


class UtilTest(unittest.TestCase):
    def test_num2date(self):
        # From Precip
        # -----------
        self.assertEqual(datetime(1987, 1, 1, 0, 0),
                         netCDF4.num2date(numpy.array([147636.0], dtype=numpy.float32), 'days since 1582-10-15 00:00', 'gregorian'))
        # From BurntArea
        # --------------
        # todo - check why in the file we have units='days since 1582-10-14 00:00' which is one day less than
        # actual start of gregorian calendar!
        # Panoply result: 155297.0 --> 2008-01-01
        self.assertEqual(datetime(2008, 1, 1, 0, 0),
                         netCDF4.num2date(155297.0, 'days since 1582-10-24 00:00', 'gregorian'))
        # netCDF4 result: ValueError: impossible date (falls in gap between end of Julian calendar and beginning of Gregorian calendar
        # self.assertEqual(datetime(2008, 1, 1, 0, 0), netCDF4.num2date(155297.0, 'days since 1582-10-14 00:00', 'gregorian'))
