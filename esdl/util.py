"""
Various utility constants, functions and classes.
Developer note: make sure this module does not import any other esdl module!
"""
import gzip

import math
import os
from abc import abstractmethod, ABCMeta
from datetime import datetime, timedelta

import netCDF4
import xarray
import numpy


def temporal_weight(a1, a2, b1, b2):
    """
    Compute a weight (0.0 to 1.0) from the overlap of time range *a1*...*a2* with time range *b1*...*b2*.
    If there is no overlap at all, return 0.

    The parameters **a1**, **a2**, **b1**, **b2** are scalar values and must all be of the same numeric type or one
    of the same time types defined in standard datetime module.

    :param a1: start of first range
    :param a2: end of first range
    :param b1: start of second range
    :param b2: end of second range

    :return: a weight between 0.0 to 1.0 (inclusively) representing the overlap of range a with range b.
    """
    a1_in_b_range = b1 <= a1 <= b2
    a2_in_b_range = b1 <= a2 <= b2
    if a1_in_b_range and a2_in_b_range:
        return 1.0
    if a1_in_b_range:
        return (b2 - a1) / (b2 - b1)
    if a2_in_b_range:
        return (a2 - b1) / (b2 - b1)
    b1_in_a_range = a1 <= b1 <= a2
    b2_in_a_range = a1 <= b2 <= a2
    if b1_in_a_range and b2_in_a_range:
        return 1.0
    return 0.0


def aggregate_images(images, weights=None):
    """
    Aggregates the list of optionally masked *images* by averaging them using the optional *weights*.

    :param images: sequence of 2-D images (numpy array-like objects)
    :param weights: a weight 0..1 for each image
    :return: A combined, masked image.
    """
    reshaped_images = []
    for i in range(len(images)):
        image = images[i]
        reshaped_image = image.reshape((1,) + image.shape)
        reshaped_images.append(reshaped_image)

    image_stack = numpy.ma.concatenate(reshaped_images)
    return numpy.ma.average(image_stack, axis=0, weights=weights)

    # aggregated_images = numpy.ma.zeros(images[0].shape,dtype = numpy.float32)
    # for i in range(len(images)):
    #     image = images[i].astype(numpy.float32)
    #     if weights:
    #         numpy.multiply(image,weights[i],out = image, casting = 'same_kind')
    #     aggregated_images += image * 1./(len(images))
    #     numpy.add(aggregated_images, image * 1./(len(images)),out = aggregated_images)
    # return aggregated_images


def resolve_temporal_range_index(target_start_year: int,
                                 target_end_year: int,
                                 temporal_res: int,
                                 source_start_time: datetime,
                                 source_end_time: datetime):
    """
    Resolve the time index of the given date range inside the given year range with the given temporal resolution.
    One sample application is to resolve the start end end time index of a certain dataset relative to the cube range.
    This is in the end useful for creating a harmonised xarray dataset.

    :param target_start_year: the start year
    :param target_end_year: the end year
    :param temporal_res: the temporal resolution (in day(s))
    :param source_start_time: the datetime to find the start time index
    :param source_end_time: the datetime to find the end time index
    :return: a tuple of start time index and end time index
    """
    time_steps = _get_time_steps(target_end_year, target_start_year, temporal_res)
    start_time_index = 0
    end_time_index = len(time_steps) - 1
    for time_index in range(len(time_steps)):
        time_1, time_2 = time_steps[time_index]
        if time_1 <= source_start_time <= time_2:
            start_time_index = time_index
        if time_1 <= source_end_time <= time_2:
            end_time_index = time_index
        if start_time_index != 0 and end_time_index != len(time_steps) - 1:
            break
    return start_time_index, end_time_index


def _get_time_steps(target_end_year, target_start_year, temporal_res):
    time_steps = []
    for target_year in range(target_start_year, target_end_year + 1):
        time_min = datetime(target_year, 1, 1)
        time_max = datetime(target_year + 1, 1, 1)
        time_1 = time_min
        num_periods_per_year = math.ceil(365.0 / temporal_res)
        for time_index in range(num_periods_per_year):
            d_time = timedelta(days=temporal_res)
            time_2 = time_1 + d_time
            if time_2 > time_max:
                time_2 = time_max
            time_steps.append((time_1, time_2))
            time_1 = time_2
    return time_steps


class DatasetCache(metaclass=ABCMeta):
    """
    A cache for datasets. A dataset is considered being a dictionary that maps variable names (str)
    to numpy.ndarray-like objects (numeric N-D arrays supporting N-D subscript indexes).
    A dataset must also provide a no-args close() method.

    Datasets are cached the CAB-LAB user data folder **cache_base_dir**/**name**.

    :param name: A name for the cache.
    :param cache_base_dir: Cache base directory. Defaults to ~/.esdl.
    """

    def __init__(self, name, cache_base_dir=None):
        if cache_base_dir is None:
            cache_base_dir = os.path.join(os.path.join(os.path.expanduser("~"), '.esdl'), 'cache')
        self._cache_dir = os.path.join(cache_base_dir, name)
        self._file_to_dataset = dict()

    @abstractmethod
    def get_dataset_variable(self, file: str, name: str, time_index: int):
        pass

    @abstractmethod
    def open_dataset(self, file):
        """
        Open a dataset. Never call this method directly.
        :param file: The file path to open.
        :return: a dataset object.
        """
        pass

    def get_dataset(self, file):
        """
        Get a cached dataset for given file path. May call **open_dataset()** if dataset is not yet cached.
        :param file: The file path.
        :return: A cached dataset
        """
        dataset = self.get_cached_dataset(file)
        if dataset is None:
            root, ext = os.path.splitext(file)
            if ext == '.gz':
                real_file = self._get_unpacked_file(file)
            else:
                real_file = file
            dataset = self.open_dataset(real_file)
            self._file_to_dataset[file] = dataset
        return dataset

    def get_cached_dataset(self, file):
        """
        Get a cached dataset for the file path.
        :param file: The file path.
        :return: The cached dataset or **None**.
        """
        return self._file_to_dataset.get(file, None)

    def close_dataset(self, file):
        """
        Close a dataset for the given file.
        :param file: The file path.
        """
        dataset = self.get_cached_dataset(file)
        if dataset is not None:
            dataset.close()
            del self._file_to_dataset[file]

    def close_all_datasets(self):
        files = list(self._file_to_dataset.keys())
        for file in files:
            self.close_dataset(file)

    def _get_unpacked_file(self, file):
        root, _ = os.path.splitext(file)
        filename = os.path.basename(root)
        real_file = os.path.join(self._cache_dir, filename)
        if not os.path.exists(real_file):
            if not os.path.exists(self._cache_dir):
                os.makedirs(self._cache_dir, exist_ok=True)
            with gzip.open(file, 'rb') as istream:
                with open(real_file, 'wb') as ostream:
                    ostream.write(istream.read())
        return real_file


class NetCDFDatasetCache(DatasetCache):
    def __init__(self, name, cache_base_dir=None):
        super(NetCDFDatasetCache, self).__init__(name, cache_base_dir=cache_base_dir)

    def get_dataset_variable(self, file: str, name: str, time_index: int) -> numpy.ndarray:
        var = self.get_dataset(file).variables[name]
        if len(var.shape) == 2:
            return var[:, :]
        else:
            raise ValueError("Error: wrong dimension for netCDF4 var. Should be 2 is " + str(len(var.shape)))

    def open_dataset(self, real_file) -> netCDF4.Dataset:
        if os.path.isfile(real_file):
            return netCDF4.Dataset(real_file)
        else:
            print('Warning: Input file (\'%s\') does not exist!' %
                  real_file)


class XarrayDatasetCache(DatasetCache):
    def __init__(self, name, cache_base_dir=None):
        super().__init__(name, cache_base_dir=cache_base_dir)

    def get_dataset_variable(self, file: str, name: str, time_index: int) -> numpy.ndarray:
        var = self.get_dataset(file).variables[name]
        if len(var.shape) == 3:
            # need to slice in order to get the correct shape of teh return variable
            var = var[time_index, :, :]
            return numpy.ma.masked_invalid(var, copy=False)
        else:
            raise ValueError("Error: wrong dimension for xarray var. Should be 3 is " + str(len(var.shape)))

    def open_dataset(self, real_file) -> xarray.Dataset:
        import cate.ops
        if os.path.isfile(real_file):
            return cate.ops.read_netcdf(real_file)
        else:
            print('Warning: Input file (\'%s\') does not exist!' %
                  real_file)


class Config:
    """
    Global ESDL configuration.

    :param cube_sources_root: The root directory for the Cube's source data files.
    """

    # The default file name for CAB-LAB configurations
    DEFAULT_FILE_NAME = 'esdl-config.py'

    _INSTANCE = None

    def __init__(self, cube_sources_root=''):
        # The root directory for the Cube's source data files
        self.cube_sources_root = cube_sources_root

    def get_cube_source_path(self, *paths):
        """
        Gets a path into the Cube's source data directory.

        :param paths: paths to be appended to the value of the *cube_sources_path* configuration parameter.
        :return: A path into the Cube's source directory.
        """
        return os.path.join(self.cube_sources_root, *paths)

    @staticmethod
    def instance():
        """
        :return: The ESDL configuration singleton.
        """
        if Config._INSTANCE is None:
            config = None
            if os.path.exists(Config.DEFAULT_FILE_NAME):
                config = Config._load(Config.DEFAULT_FILE_NAME)
            else:
                dir_path = os.path.dirname(__file__)
                while os.path.exists(dir_path):
                    config_file = os.path.abspath(os.path.join(dir_path, Config.DEFAULT_FILE_NAME))
                    if os.path.exists(config_file):
                        config = Config._load(config_file)
                        break
                    setup_py = os.path.join(dir_path, 'setup.py')
                    if os.path.exists(setup_py):
                        break
                    dir_path = os.path.join(dir_path, '..')
                if config is None:
                    config = Config()
                    print('Warning: no ESDL configuration file (\'%s\') found in any known directory' %
                          Config.DEFAULT_FILE_NAME)
            Config._INSTANCE = config
        return Config._INSTANCE

    @staticmethod
    def _load(file_path):
        config = Config()
        with open(file_path, 'r') as fp:
            python_code = fp.read()
        exec(python_code, None, config.__dict__)
        print('ESDL configuration loaded from %s' % file_path)
        return config
