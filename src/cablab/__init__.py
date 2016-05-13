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

from cablab.cube import Cube
from cablab.cube import CubeData
from cablab.cube_config import CUBE_MODEL_VERSION
from cablab.cube_config import CubeConfig
from cablab.cube_config import __version__
from cablab.cube_provider import BaseCubeSourceProvider
from cablab.cube_provider import CubeSourceProvider
from cablab.cube_provider import NetCDFCubeSourceProvider
from cablab.cube_provider import TestCubeSourceProvider

__author__ = 'Brockmann Consult GmbH'

__all__ = [
    'BaseCubeSourceProvider',
    'NetCDFCubeSourceProvider',
    'TestCubeSourceProvider',
    'CUBE_MODEL_VERSION',
    'Cube',
    'CubeConfig',
    'CubeData',
    'CubeSourceProvider',
    'SOURCE_PROVIDERS',
]
