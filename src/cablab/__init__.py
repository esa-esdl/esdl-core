"""
The CAB-LAB parent module.
"""
__author__ = 'Brockmann Consult GmbH'

import netCDF4
from pkg_resources import iter_entry_points

from cablab.cube import ImageProvider
from cablab.cube import BaseImageProvider
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


def _load_image_providers():
    image_provider_classes = dict()
    for entry_point in iter_entry_points(group='cablab.image_providers', name=None):
        image_provider_class = entry_point.load()
        # TODO: Check that it is a class type and that it has our expected interface
        image_provider_classes[entry_point.name] = image_provider_class
    return image_provider_classes


IMAGE_PROVIDERS = _load_image_providers()

__all__ = ['ImageProvider',
           'BaseImageProvider',
           'CubeConfig',
           'Cube',
           'date2num',
           'num2date',
           'IMAGE_PROVIDERS',
           'TIME_UNITS',
           'TIME_CALENDAR']
