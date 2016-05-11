"""
Various utility constants, functions and classes.
Developer note: make sure this module does not import any other cablab module!
"""

import gzip
import os

import netCDF4
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
        if weights:
            reshaped_image *= weights[i]
        reshaped_images.append(reshaped_image)
    image_stack = numpy.ma.concatenate(reshaped_images)
    return numpy.ma.average(image_stack, axis=0)


class NetCDFDatasetCache:
    def __init__(self, name, cache_base_dir=None):
        if cache_base_dir is None:
            cache_base_dir = os.path.join(os.path.join(os.path.expanduser("~"), '.cablab'), 'cache')
        self.cache_dir = os.path.join(cache_base_dir, name)
        self.file_to_dataset = dict()

    def get_dataset(self, file):
        if file in self.file_to_dataset:
            dataset = self.file_to_dataset[file]
        else:
            root, ext = os.path.splitext(file)
            if ext == '.gz':
                real_file = self._get_unpacked_file(file)
            else:
                real_file = file
            dataset = netCDF4.Dataset(real_file)
            self.file_to_dataset[file] = dataset
        return dataset

    def close_dataset(self, file):
        if file not in self.file_to_dataset:
            return
        dataset = self.file_to_dataset[file]
        dataset.close()
        del self.file_to_dataset[file]

    def close_all_datasets(self):
        files = list(self.file_to_dataset.keys())
        for file in files:
            self.close_dataset(file)

    def _get_unpacked_file(self, file):
        root, _ = os.path.splitext(file)
        filename = os.path.basename(root)
        real_file = os.path.join(self.cache_dir, filename)
        if not os.path.exists(real_file):
            if not os.path.exists(self.cache_dir):
                os.makedirs(self.cache_dir, exist_ok=True)
            with gzip.open(file, 'rb') as istream:
                with open(real_file, 'wb') as ostream:
                    ostream.write(istream.read())
        return real_file


# todo - use as mixin class in each provider
class NetCDFDatasetCacheSupport:
    """
    Mixin class whose intended use to add NetCDFDatasetCache support to a CubeSourceProvider implementation.
    """
    def __init__(self, name, cache_base_dir=None):
        self._dataset_cache = NetCDFDatasetCache(name, cache_base_dir=cache_base_dir)
        self._old_indices = None

    @property
    def dataset_cache(self):
        return self._dataset_cache

    def close(self):
        self._dataset_cache.close_all_datasets()
        self._old_indices = None


class Config:
    """
    Global CAB-LAB configuration.

    :param cube_sources_root: The root directory for the Cube's source data files.
    """

    # The default file name for CAB-LAB configurations
    DEFAULT_FILE_NAME = 'cablab-config.py'

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
        :return: The CAB-LAB configuration singleton.
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
                    print('Warning: no CAB-LAB configuration file (\'%s\') found in any known directory' %
                          Config.DEFAULT_FILE_NAME)
            Config._INSTANCE = config
        return Config._INSTANCE

    @staticmethod
    def _load(file_path):
        config = Config()
        with open(file_path, 'r') as fp:
            python_code = fp.read()
        exec(python_code, None, config.__dict__)
        print('CAB-LAB configuration loaded from %s' % file_path)
        return config
