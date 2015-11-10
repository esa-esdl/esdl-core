"""
Test some properties of the netCDF4 library.
"""
import time
from datetime import datetime
from unittest import TestCase

import netCDF4
import numpy


class NetCDF4Test(TestCase):
    def test_num2date(self):
        # From Precip
        # -----------
        self.assertEqual(datetime(1987, 1, 1, 0, 0),
                         netCDF4.num2date(numpy.array([147636.0], dtype=numpy.float32), 'days since 1582-10-15 00:00',
                                          'gregorian'))
        # From BurntArea
        # --------------
        # Check why in the file we have units='days since 1582-10-14 00:00' which is one day less than
        # actual start of gregorian calendar!
        # Panoply result: 155297.0 --> 2008-01-01
        #
        # Resolution: Fabian told us that units='days since 1582-10-14 00:00' is an error in the MPI netCDF files.
        #
        self.assertEqual(datetime(2008, 1, 1, 0, 0),
                         netCDF4.num2date(155297.0, 'days since 1582-10-24 00:00', 'gregorian'))
        # netCDF4 result: ValueError: impossible date (falls in gap between end of Julian calendar and beginning of Gregorian calendar
        # self.assertEqual(datetime(2008, 1, 1, 0, 0), netCDF4.num2date(155297.0, 'days since 1582-10-14 00:00', 'gregorian'))

    def test_that_empty_variables_are_filled_with_fill_values(self):
        ds = netCDF4.Dataset('test.nc', mode='w', format='NETCDF4_CLASSIC')
        ds.createDimension('d1', 4)
        ds.createVariable('v1', 'f4', dimensions=('d1',), fill_value=-9999.0)
        ds.close()

        ds = netCDF4.Dataset('test.nc')
        var = ds.variables['v1']
        array = var[:]
        ds.close()

        self.assertTrue(numpy.ma.is_masked(array))
        self.assertIs(numpy.ma.masked, array[0], msg='at index 0')
        self.assertIs(numpy.ma.masked, array[1], msg='at index 1')
        self.assertIs(numpy.ma.masked, array[2], msg='at index 2')
        self.assertIs(numpy.ma.masked, array[3], msg='at index 3')

    def test_that_fill_value_from_netcdf_works_with_numpy_ma(self):
        ds = netCDF4.Dataset('test.nc', mode='w', format='NETCDF4_CLASSIC')
        ds.createDimension('d1', 4)
        var = ds.createVariable('v1', 'f4', dimensions=('d1',), fill_value=-9999.0)
        var[:] = numpy.array([1.0, -9999.0, 3.0, numpy.NaN])
        ds.close()

        ds = netCDF4.Dataset('test.nc')
        var = ds.variables['v1']
        array = var[:]
        ds.close()

        # Test: The netCDF4 module will not automatically mask NaN values
        self.assertTrue(numpy.ma.is_masked(array))
        self.assertEqual(1.0, array[0], msg='at index 0')
        self.assertIs(numpy.ma.masked, array[1], msg='at index 1')
        self.assertEqual(3.0, array[2], msg='at index 2')
        self.assertTrue(numpy.isnan(array[3]), msg='at index 3')

        # Test: The netCDF4 module returns a masked array that can be used in expressions
        new_array = array + numpy.ones(4)
        self.assertTrue(numpy.ma.is_masked(new_array))
        self.assertEqual(2.0, new_array[0], msg='at index 0')
        self.assertIs(numpy.ma.masked, new_array[1], msg='at index 1')
        self.assertEqual(4.0, new_array[2], msg='at index 2')
        self.assertTrue(numpy.isnan(new_array[3]), msg='at index 3')

        # Test: Mask invalid in the netCDF4 masked array
        new_array = numpy.ma.masked_invalid(array, copy=False)
        self.assertTrue(numpy.ma.is_masked(new_array))
        self.assertEqual(1.0, new_array[0], msg='at index 0')
        self.assertIs(numpy.ma.masked, new_array[1], msg='at index 1')
        self.assertEqual(3.0, new_array[2], msg='at index 2')
        self.assertIs(numpy.ma.masked, new_array[3], msg='at index 3')

        # Test: Fill masked values in the netCDF4 masked array with the NetCDF '_FillValue'
        new_array = array.filled()
        self.assertFalse(numpy.ma.is_masked(new_array))
        self.assertEqual(1.0, new_array[0], msg='at index 0')
        self.assertEqual(-9999.0, new_array[1], msg='at index 1')
        self.assertEqual(3.0, new_array[2], msg='at index 2')
        self.assertTrue(numpy.isnan(new_array[3]), msg='at index 3')

        # Test: Fill masked values in the netCDF4 masked array with NaN
        new_array = array.filled(numpy.NaN)
        self.assertFalse(numpy.ma.is_masked(new_array))
        self.assertEqual(1.0, new_array[0], msg='at index 0')
        self.assertTrue(numpy.isnan(new_array[1]), msg='at index 1')
        self.assertEqual(3.0, new_array[2], msg='at index 2')
        self.assertTrue(numpy.isnan(new_array[3]), msg='at index 3')

        # Test: Apply a numpy array method (e.g. kron)
        new_array = numpy.kron(array, numpy.ones((2,)))
        self.assertFalse(numpy.ma.is_masked(new_array))
        self.assertEqual(8, len(new_array))
        self.assertEqual(1.0, new_array[0], msg='at index 0')
        self.assertEqual(1.0, new_array[1], msg='at index 1')
        self.assertEqual(-9999.0, new_array[2], msg='at index 2')
        self.assertEqual(-9999.0, new_array[3], msg='at index 3')
        self.assertEqual(3.0, new_array[4], msg='at index 4')
        self.assertEqual(3.0, new_array[5], msg='at index 5')
        self.assertTrue(numpy.isnan(new_array[6]), msg='at index 6')
        self.assertTrue(numpy.isnan(new_array[7]), msg='at index 7')

    def chunking_test(self):
        names = [
            'test-chunk-none.nc',
            # 'test-chunk-1.720.1440.nc',
            # 'test-chunk-460.18.36.nc',
            # 'test-chunk-460.720.1.nc',
            # 'test-chunk-460.1.1440.nc',
        ]
        chunks = [
            None,
            (1, 720, 1440),
            (460, 18, 36),
            (460, 720, 1),
            (460, 1, 1440),
        ]
        for i in range(len(names)):
            print('Creating ' + names[i] + "...")
            self._create_ds(names[i], chunks[i])

        import random
        self._x = [0] * 100
        self._y = [0] * 100
        for i in range(100):
            self._x[i] = int(100 * random.random())
            self._y[i] = int(100 * random.random())

        for name in names:
            self._test_it('test_1', name, self.__test_1)
        for name in names:
            self._test_it('test_2', name, self.__test_2)
        for name in names:
            self._test_it('test_3', name, self.__test_3)
        for name in names:
            self._test_it('test_4', name, self.__test_4)
        for name in names:
            self._test_it('test_5', name, self.__test_5)

    def _test_it(self, test_name, file, test_fn):
        print('%s, %s...' % (test_name, file))
        ds = netCDF4.Dataset(file)
        v = ds.variables['v']
        t1 = time.time()
        test_fn(v)
        t2 = time.time()
        ds.close()
        print('%s, %s, time: %f s' % (test_name, file, t2 - t1))

    def __test_1(self, v):
        for y in range(10):
            for x in range(10):
                z = v[:, y, x]
                self.___process(z)

    def __test_2(self, v):
        for y in range(100):
            z = v[:, y, 1]
            self.___process(z)

    def __test_3(self, v):
        for x in range(100):
            z = v[:, 1, x]
            self.___process(z)

    def __test_4(self, v):
        for i in range(100):
            z = v[:, i, i]
            self.___process(z)

    def __test_5(self, v):
        for i in range(100):
            z = v[:, self._y[i], self._x[i]]
            self.___process(z)

    def ___process(self, z):
        pass

    def _create_ds(self, name, chunksizes):
        ds = netCDF4.Dataset(name, mode='w', format='NETCDF4_CLASSIC')
        ds.createDimension('time', 460)
        ds.createDimension('lat', 720)
        ds.createDimension('lon', 1440)
        v = ds.createVariable('v', numpy.float32, ('time', 'lat', 'lon'),
                              fill_value=-9999.,
                              chunksizes=chunksizes)
        for i in range(460):
            v[i, :, :] = numpy.zeros((720, 1440), numpy.float32)
        ds.close()
