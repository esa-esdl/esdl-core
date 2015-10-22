"""
The CAB-LAB parent module.
"""
__author__ = 'Brockmann Consult GmbH'

import netCDF4

from cablab.cube import CubeConfig
from cablab.cube import Cube

TIME_UNITS = 'days since 0001-01-01 00:00:00.0'
TIME_CALENDAR = 'standard'


def date2num(dates):
    """
    Return numeric time values given datetime objects.

    >>> from datetime import datetime
    >>> date2num([datetime(2015, 10, 22), datetime(2000, 1, 1)])
    array([ 735894.,  730121.])

    :param dates: datetime.datetime values
    :return: numeric time values
    """
    return netCDF4.date2num(dates,
                            units=TIME_UNITS,
                            calendar=TIME_CALENDAR)


def num2date(times):
    """
    Return datetime objects given numeric time values.

    >>> num2date([735894., 730121.])
    array([datetime.datetime(2015, 10, 22, 0, 0),
           datetime.datetime(2000, 1, 1, 0, 0)], dtype=object)

    :param times: numeric time values
    :return: datetime.datetime values
    """
    return netCDF4.num2date(times,
                            units=TIME_UNITS,
                            calendar=TIME_CALENDAR)


__all__ = ['CubeConfig',
           'Cube',
           'date2num',
           'num2date']
