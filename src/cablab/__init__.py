"""

Data Cube read-only access::

    from cablab import Cube
    from datetime import datetime
    cube = Cube.open('./cablab-cube-v05')
    data = cube.data.get(['LAI', 'Precip'], [datetime(2001, 6, 1), datetime(2012, 1, 1)], 53.2, 12.8)

Data Cube creation/update::

    from cablab import Cube, CubeConfig
    from datetime import datetime
    cube = Cube.create('./my-cablab-cube', CubeConfig(spatial_res=0.05))
    cube.update(MyVar1SourceProvider(cube.config, './my-cube-sources/var1'))
    cube.update(MyVar2SourceProvider(cube.config, './my-cube-sources/var2'))

"""

from pkg_resources import iter_entry_points

from cablab.cube import BaseCubeSourceProvider
from cablab.cube import Cube
from cablab.cube import CubeConfig
from cablab.cube import CubeData
from cablab.cube import CubeSourceProvider

__author__ = 'Brockmann Consult GmbH'


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

__all__ = [
    'Cube',
    'CubeConfig',
    'CubeData',
    'CubeSourceProvider',
    'BaseCubeSourceProvider',
    'SOURCE_PROVIDERS',
]
