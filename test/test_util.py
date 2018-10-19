import unittest

import numpy
from netCDF4 import Dataset, date2num
from numpy.random import uniform
from datetime import timedelta

from esdl.util import temporal_weight, NetCDFDatasetCache, XarrayDatasetCache
from esdl.util import resolve_temporal_range_index
from esdl.util import aggregate_images

from datetime import datetime


def module_exists(module_name):
    try:
        __import__(module_name)
    except ImportError:
        return False
    else:
        return True


def generate_test_netcdf4(has_time: bool = False, fn: str = 'test.nc') -> str:
    dataset = Dataset(fn, 'w', format='NETCDF4_CLASSIC')
    lat = dataset.createDimension('lat', 180)
    lon = dataset.createDimension('lon', 360)

    latitudes = dataset.createVariable('latitude', numpy.float32, ('lat',))
    longitudes = dataset.createVariable('longitude', numpy.float32, ('lon',))
    if has_time:
        time = dataset.createDimension('time', None)
        temp = dataset.createVariable('temperature', numpy.float32, ('time', 'lat', 'lon'))
    else:
        temp = dataset.createVariable('temperature', numpy.float32, ('lat', 'lon'))

    latitudes.units = 'degree_north'
    longitudes.units = 'degree_east'
    temp.units = 'K'

    latitudes[:] = numpy.arange(-90, 90, 1)
    longitudes[:] = numpy.arange(-180, 180, 1)
    nlats = len(dataset.dimensions['lat'])
    nlons = len(dataset.dimensions['lon'])

    if has_time:
        temp[0:5, :, :] = uniform(size=(5, nlats, nlons))

        times = dataset.createVariable('time', numpy.float64, ('time',))
        times.units = 'hours since 0001-01-01 00:00:00'
        times.calendar = 'gregorian'

        dates = []
        for n in range(temp.shape[0]):
            dates.append(datetime(2001, 3, 1) + n * timedelta(hours=12))

        times[:] = date2num(dates, units=times.units, calendar=times.calendar)
    else:
        temp[:, :] = uniform(size=(nlats, nlons))

    dataset.close()

    return fn


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
        self.assertAlmostEqual(im[0][1], (0.5 * 2.1 + 0.25 * 4.3) / 0.75, places=4)
        self.assertIs(im[1][0], numpy.ma.masked)
        self.assertAlmostEqual(im[1][1], (0.5 * 4.1 + 1.0 * 5.2 + 0.25 * 6.3) / 1.75, places=3)

        im1 = numpy.zeros((3, 3))
        im2 = numpy.ones((3, 3))

        im = aggregate_images((im1, im2), weights=(0.25, 0.75))

        self.assertEqual(im[0][0], 0.75)

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

    @unittest.skipUnless(module_exists("cate"), "Could not load cate. Skip dataset cache test.")
    def test_datasetcache(self):
        netcdf_cache = NetCDFDatasetCache('test')
        xarray_cache = XarrayDatasetCache('test')

        file_netcdf = generate_test_netcdf4(has_time=False, fn='test_netcdf.nc')
        file_xarray = generate_test_netcdf4(has_time=True, fn='test_xarray.nc')

        # Test shape correct by passing a 3dim netcdf into the netcdf cache (needs dim2)
        with self.assertRaises(ValueError):
            netcdf_cache.get_dataset_variable(file_xarray, 'temperature', 0)

        # Test shape correct by passing a 2dim netcdf into the xarray cache (needs dim3)
        with self.assertRaises(ValueError):
            xarray_cache.get_dataset_variable(file_netcdf, 'temperature', 0)