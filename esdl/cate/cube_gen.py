from abc import ABCMeta

import numpy
import xarray
import os
import cate.ops

from esdl import CubeConfig
from esdl.cube_provider import DatasetCubeSourceProvider
from esdl.util import DatasetCache


class CateDatasetCache(DatasetCache):
    """
    :param name: A name for the cache.
    :param cache_base_dir: Cache base directory. Defaults to ~/.esdl.
    """

    def __init__(self, name, cache_base_dir=None):
        super().__init__(name, cache_base_dir=cache_base_dir)

    def get_dataset_variable(self, file: str, name: str, time_index: int) -> numpy.ndarray:
        var = self.get_dataset(file).variables[name]
        if len(var.shape) == 3:
            # need to slice in order to get the correct shape of the return variable
            var = var[time_index, :, :]
            return numpy.ma.masked_invalid(var, copy=False)
        else:
            raise ValueError("Error: wrong dimension for xarray var. Should be 3 is " + str(len(var.shape)))

    def open_dataset(self, real_file) -> xarray.Dataset:
        if os.path.isfile(real_file):
            return cate.ops.read_netcdf(real_file)
        else:
            print('Warning: Input file (\'%s\') does not exist!' %
                  real_file)


class CateCubeSourceProvider(DatasetCubeSourceProvider[CateDatasetCache], metaclass=ABCMeta):
    """
    This Cube Source Provider uses a NetCDFDatasetProvider dataset cache.
    :param cube_config: Specifies the fixed layout and conventions used for the cube.
    :param name: The provider's registration name.
    :param dir_path: Source directory to read the files from. If relative path,
           it will be resolved against the **cube_sources_root** path of the
           global ESDL configuration (**esdl.util.Config.instance()**).
    :param resampling_order: The order in which resampling is performed. One of 'time_first', 'space_first'.
    """

    def __init__(self, cube_config: CubeConfig, name: str, dir_path: str, resampling_order: str):
        super().__init__(CateDatasetCache(name), cube_config, name, dir_path, resampling_order)