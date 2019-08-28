"""

Data Cube read-only access::

    from esdl import Cube
    from datetime import datetime
    cube = Cube.open('./esdl-cube-v05')
    data = cube.data.get(['LAI', 'Precip'], [datetime(2001, 6, 1), datetime(2012, 1, 1)], 53.2, 12.8)

Data Cube creation/update::

    from esdl import Cube, CubeConfig
    from datetime import datetime
    cube = Cube.create('./my-esdl-cube', CubeConfig(spatial_res=0.05))
    cube.update(MyVar1SourceProvider(cube.config, './my-cube-sources/var1'))
    cube.update(MyVar2SourceProvider(cube.config, './my-cube-sources/var2'))

"""

from .version import version as __version__
from .cube import Cube
from .cube_config import CUBE_MODEL_VERSION
from .cube_config import CubeConfig
# from .cube_provider import CubeSourceProvider
# from .cube_provider import BaseCubeSourceProvider
# from .cube_provider import NetCDFCubeSourceProvider
# from .cube_provider import BaseStaticCubeSourceProvider
# from .cube_provider import NetCDFStaticCubeSourceProvider
# from .cube_provider import TestCubeSourceProvider

from .cube_store import CubeStore
from .cube_store import CubesStore
from .cube_provider import CubeSourceProvider

__author__ = 'Brockmann Consult GmbH'

__all__ = [
    # 'BaseCubeSourceProvider',
    # 'BaseStaticCubeSourceProvider',
    # 'NetCDFCubeSourceProvider',
    # 'NetCDFStaticCubeSourceProvider',
    # 'TestCubeSourceProvider',
    'CUBE_MODEL_VERSION',
    'Cube',
    'CubeConfig',
    'CubeStore',
    'CubesStore',
    'CubeSourceProvider',
]
