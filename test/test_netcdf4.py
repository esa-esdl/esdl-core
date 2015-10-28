"""
Test some properties of the netCDF4 library.
"""
from unittest import TestCase

import netCDF4
import numpy


class NetCDF4Test(TestCase):
    def test_how_fill_value_is_handled_by_library(self):
        ds = netCDF4.Dataset('test.nc', mode='w', format='NETCDF4')
        ds.createDimension('d1', 5)
        var = ds.createVariable('v1', 'f4', dimensions=('d1',), fill_value=-9999.0)
        var[:] = numpy.array([1.0, -9999.0, 3.0, numpy.NaN, 5.0])
        ds.close()

        ds = netCDF4.Dataset('test.nc')
        var = ds.variables['v1']
        data = var[:]
        ds.close()

        self.assertTrue(numpy.ma.is_masked(data))
        self.assertEqual(1.0, data[0], msg='at index 0')
        self.assertIs(numpy.ma.masked, data[1], msg='at index 2')
        self.assertEqual(3.0, data[2], msg='at index 3')
        self.assertTrue(numpy.isnan(data[3]), msg='at index 4')
        self.assertEqual(5.0, data[4], msg='at index 5')

        data2 = data + numpy.ones(5)

        self.assertTrue(numpy.ma.is_masked(data2))
        self.assertEqual(2.0, data2[0], msg='at index 0')
        self.assertIs(numpy.ma.masked, data2[1], msg='at index 2')
        self.assertEqual(4.0, data2[2], msg='at index 3')
        self.assertTrue(numpy.isnan(data2[3]), msg='at index 4')
        self.assertEqual(6.0, data2[4], msg='at index 5')
