"""
Test some properties of the netCDF4 library.
"""
from unittest import TestCase

import netCDF4
import numpy


class NetCDF4Test(TestCase):
    def test_that_fill_value_from_netcdf_works_with_numpy_ma(self):
        ds = netCDF4.Dataset('test.nc', mode='w', format='NETCDF4')
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

        # Test: Fill masked values in the netCDF4 masked array
        new_array = array.filled(numpy.NaN)
        self.assertFalse(numpy.ma.is_masked(new_array))
        self.assertEqual(1.0, new_array[0], msg='at index 0')
        self.assertTrue(numpy.isnan(new_array[1]), msg='at index 1')
        self.assertEqual(3.0, new_array[2], msg='at index 2')
        self.assertTrue(numpy.isnan(new_array[3]), msg='at index 3')
