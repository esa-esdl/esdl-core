"""
The CAB-LAB parent module.
"""

__author__ = 'Brockmann Consult GmbH'

from pkg_resources import iter_entry_points

from cablab.cube import CubeSourceProvider
from cablab.cube import BaseCubeSourceProvider
from cablab.cube import CubeConfig
from cablab.cube import Cube
from cablab.util import TIME_CALENDAR
from cablab.util import TIME_UNITS
from cablab.util import date2num
from cablab.util import num2date


def _load_source_providers():
    source_provider_classes = dict()
    for entry_point in iter_entry_points(group='cablab.source_providers', name=None):
        source_provider_class = entry_point.load()
        if issubclass(source_provider_class, CubeSourceProvider):
            source_provider_classes[entry_point.name] = source_provider_class
        else:
            print('warning: cablab.source_providers: requires a \'%s\' but got a \'%s\'' % (
            CubeSourceProvider, type(source_provider_class)))
    return source_provider_classes


SOURCE_PROVIDERS = _load_source_providers()

__all__ = ['CubeSourceProvider',
           'BaseCubeSourceProvider',
           'CubeConfig',
           'Cube',
           'date2num',
           'num2date',
           'SOURCE_PROVIDERS',
           'TIME_UNITS',
           'TIME_CALENDAR']
