import glob
import os.path
import time
from abc import ABCMeta, abstractmethod, abstractproperty
from datetime import datetime

import gridtools.resampling as gtr
import netCDF4
import numpy as np
from typing import Tuple, Dict, Any

from .cube_config import CubeConfig
from .util import Config, NetCDFDatasetCache, aggregate_images, temporal_weight


def _get_us_method(var_attributes):
    return gtr.__dict__['US_' + var_attributes.get('us_method', 'NEAREST')]


def _get_ds_method(var_attributes):
    return gtr.__dict__['DS_' + var_attributes.get('ds_method', 'MEAN')]


class CubeSourceProvider(metaclass=ABCMeta):
    """
    An abstract interface for objects representing data source providers for the data cube.
    Cube source providers are passed to the :py:meth:`Cube.update` method.

    :param cube_config: Specifies the fixed layout and conventions used for the cube.
    :param name: The provider's registration name.
    """

    def __init__(self, cube_config: CubeConfig, name: str):
        if not cube_config:
            raise ValueError('cube_config expected')
        if not name:
            raise ValueError('name expected')
        self._name = name
        self._cube_config = cube_config

    @property
    def name(self) -> str:
        """ The provider's registration name. """
        return self._name

    @property
    def cube_config(self) -> CubeConfig:
        """ The data cube's configuration. """
        return self._cube_config

    @abstractmethod
    def prepare(self):
        """
        Called by a Cube instance's :py:meth:`update` method before any other provider methods are called.
        Provider instances should prepare themselves w.r.t. the given cube configuration *cube_config*.
        """
        pass

    @abstractproperty
    def temporal_coverage(self) -> Tuple[datetime, datetime]:
        """
        Return the start and end time of the available source data.

        :return: A tuple of datetime.datetime instances (start_time, end_time).
        """
        return None

    @abstractproperty
    def spatial_coverage(self) -> Tuple[int, int, int, int]:
        """
        Return the spatial coverage as a rectangle represented by a tuple of integers (x, y, width, height) in the
        cube's image coordinates.

        :return: A tuple of integers (x, y, width, height) in the cube's image coordinates.
        """
        return None

    @abstractproperty
    def variable_descriptors(self) -> Dict[str, Dict[str, Any]]:
        """
        Return a dictionary which maps target(!) variable names to a dictionary of target attribute values.
        The following attributes have a special meaning and shall or should be provided:

        * ``data_type``: A numpy data type. Mandatory attribute.
        * ``fill_value``: The value used for indicating missing grid cells. Mandatory attribute.
        * ``source_name``: the name of the variable in the source (files).
            Optional, defaults to the target variable's name.
        * ``scale_factor``: See CF conventions. Optional, defaults to one (``1.0``).
        * ``add_offset``: See CF conventions. Optional, defaults to zero (``0.0``).
        * ``units``: See CF conventions. Optional.
        * ``standard_name``: See CF conventions. Optional.
        * ``long_name``: See CF conventions. Optional.

        :return: dictionary of variable names to attribute dictionaries
        """
        return None

    @abstractmethod
    def compute_variable_images(self, period_start: datetime, period_end: datetime) -> Dict[str, np.ndarray]:
        """
        Return variable name to variable image mapping of all provided variables.
        Each image is a numpy array with the shape (height, width) derived from the :py:meth:`get_spatial_coverage`
        method.

        The images must be computed (by aggregation or interpolation or copy) from the source data in the given
        time period *period_start* <= source_data_time < *period_end* and taking into account other data cube
        configuration settings.

        The method is called by a Cube instance's :py:meth:`update` method for all possible time periods in the time
        range given by the :py:meth:`get_temporal_coverage` method. The times given are adjusted w.r.t. the cube's
        reference time and temporal resolution.

        :param period_start: The period start time as a datetime.datetime instance
        :param period_end: The period end time as a datetime.datetime instance

        :return: A dictionary variable name --> image. Each image must be numpy array-like object of shape
                 (grid_height, grid_width) as given by the :py:class:`CubeConfig`.
                 Return ``None`` if no such variables exists for the given target time range.
        """
        return None

    @abstractmethod
    def close(self):
        """
        Called by the cube's :py:meth:`update` method after all images have been retrieved and the provider is no
        longer used.
        """
        pass


class BaseCubeSourceProvider(CubeSourceProvider, metaclass=ABCMeta):
    """
    A partial implementation of the :py:class:`CubeSourceProvider` interface that computes its output image data
    using weighted averages. The weights are computed according to the overlap of source time ranges and a
    requested target time range.

    :param cube_config: Specifies the fixed layout and conventions used for the cube.
    :param name: The provider's registration name.
    """

    def __init__(self, cube_config: CubeConfig, name: str):
        super(BaseCubeSourceProvider, self).__init__(cube_config, name)
        self._source_time_ranges = None

    def prepare(self):
        """
        Calls **compute_source_time_ranges** and assigns the return value to the field **source_time_ranges**.
        """
        self._source_time_ranges = self.compute_source_time_ranges()

    @property
    def source_time_ranges(self):
        return self._source_time_ranges

    @property
    def spatial_coverage(self):
        """
        Return the spatial grid coverage given in the Cube's configuration (default).

        :return: A tuple of integers (x, y, width, height) in the cube's image coordinates.
        """
        return 0, 0, self.cube_config.grid_width, self.cube_config.grid_height

    @property
    def temporal_coverage(self) -> (datetime, datetime):
        """
        Return the temporal coverage derived from the value returned by **compute_source_time_ranges()**.
        """
        if len(self._source_time_ranges) > 0:
            return self._source_time_ranges[0][0], self._source_time_ranges[-1][1]
        else:
            raise KeyError("No datasets are available for the specified temporal coverage. "
                           "Consider changing the start_time or end_time in cube.config")

    @abstractmethod
    def compute_source_time_ranges(self) -> list or None:
        """
        Return a sorted list of all time ranges of every source file.
        Items in this list must be 4-element tuples of the form
        (time_start: datetime, time_stop: datetime, file: str, time_index: int).
        The method is called from the **prepare()** method in order to pre-compute all available time ranges.
        This method must be implemented by derived classes.
        """
        return None

    def compute_variable_images(self, period_start: datetime, period_end: datetime):
        """
        For each source time range that has an overlap with the given target time range compute a weight
        according to the overlapping range. Pass these weights as source index to weight mapping
        to **compute_variable_images_from_sources(index_to_weight)** and return the result.

        :return: A dictionary variable name --> image. Each image must be numpy array-like object of shape
                 (grid_height, grid_width) as given by the **CubeConfig**.
                 Return ``None`` if no such variables exists for the given target time range.
        """

        source_time_ranges = self._source_time_ranges
        if len(source_time_ranges) == 0:
            return None

        index_to_weight = dict()
        for i in range(len(source_time_ranges)):
            source_start_time, source_end_time = source_time_ranges[i][0:2]
            weight = temporal_weight(source_start_time, source_end_time,
                                     period_start, period_end)
            if weight > 0.0:
                index_to_weight[i] = weight
        if not index_to_weight:
            return None

        self.log('computing images for time range %s to %s from %d source(s)...' % (period_start, period_end,
                                                                                    len(index_to_weight)))
        t1 = time.time()
        result = self.compute_variable_images_from_sources(index_to_weight)
        t2 = time.time()
        self.log('images computed for %s, took %f seconds' % (str(list(result.keys())), t2 - t1))

        return result

    @abstractmethod
    def compute_variable_images_from_sources(self, index_to_weight: Dict[int, float]):
        """
        Compute the target images for all variables from the sources with the given time indices to weights mapping.

        The time indices in *index_to_weight* are guaranteed to point into the time ranges list returned by
        py:meth:`compute_source_time_ranges`.

        The weight values in *index_to_weight* are float values computed from the overlap of source time ranges with
        a requested target time range.

        :param index_to_weight: A dictionary mapping time indexes --> weight values.
        :return: A dictionary variable name --> image. Each image must be numpy array-like object of shape
                 (grid_height, grid_width) as specified by the cube's layout configuration **CubeConfig**.
                 Return ``None`` if no such variables exists for the given target time range.
        """
        pass

    def log(self, message: str):
        """
        Log a *message*.

        :param message: The message to be logged.
        """
        print('%s: %s' % (self.name, message))

    def _get_file_and_time_index(self, var_index: int):
        """
        Return the file path and time dimension index as tuple.
        To be used by derived classes only.
        """
        return self._source_time_ranges[var_index][2:4]


class BaseStaticCubeSourceProvider(CubeSourceProvider, metaclass=ABCMeta):
    """
    A CubeSourceProvider that
    * uses a NetCDF source dataset read from a given *dir_path*;
    * performs only spatial resampling.

    :param cube_config: Specifies the fixed layout and conventions used for the cube.
    :param name: The provider's registration name.
    """

    def __init__(self, cube_config: CubeConfig, name: str):
        super(BaseStaticCubeSourceProvider, self).__init__(cube_config, name)
        self._variable_images_computed = False

    def prepare(self):
        """Clear the flag that indicates that the static sources have been processed."""
        self._variable_images_computed = False

    @property
    def spatial_coverage(self):
        """
        Return the spatial grid coverage given in the Cube's configuration (default).

        :return: A tuple of integers (x, y, width, height) in the cube's image coordinates.
        """
        return 0, 0, self.cube_config.grid_width, self.cube_config.grid_height

    @property
    def temporal_coverage(self) -> (datetime, datetime):
        """
        Return the temporal coverage derived from the value returned by **compute_source_time_ranges()**.
        """
        return self.cube_config.start_time, self.cube_config.end_time

    def compute_variable_images(self, period_start: datetime, period_end: datetime) -> Dict[str, np.ndarray]:
        if self._variable_images_computed:
            return None

        dataset = self.open_dataset()
        try:
            var_descriptors = self.variable_descriptors
            target_var_images = dict()
            for var_name, var_attributes in var_descriptors.items():
                source_name = var_attributes.get('source_name', var_name)
                var_image = self.get_dataset_image(dataset, source_name)
                var_image = self.transform_source_image(var_image)
                var_image = gtr.resample_2d(var_image,
                                            self.cube_config.grid_width,
                                            self.cube_config.grid_height,
                                            ds_method=_get_ds_method(var_attributes),
                                            us_method=_get_us_method(var_attributes),
                                            fill_value=var_attributes.get('fill_value', np.nan))
                if var_image.shape[1] / var_image.shape[0] != 2.0:
                    print("Warning: wrong size ratio of image in '%s'. Expected 2, got %f" % (
                        self.get_dataset_file_path(dataset),
                        var_image.shape[1] / var_image.shape[0]))
                target_var_images[var_name] = var_image

        finally:
            self.close_dataset(dataset)

        self._variable_images_computed = True
        return target_var_images

    @abstractmethod
    def open_dataset(self) -> object:
        """
        Open the single dataset and return its representation.
        :return: a dataset object
        """

    @abstractmethod
    def close_dataset(self, dataset: object):
        """
        Close *dataset*.
        :param dataset: the dataset returned by :py:meth:`open_dataset`
        """

    @abstractmethod
    def get_dataset_file_path(self, dataset: object) -> str:
        """
        Get the file path for *dataset*.
        :param dataset: the dataset returned by :py:meth:`open_dataset`
        :return: a file path
        """

    @abstractmethod
    def get_dataset_image(self, dataset: object, name: str):
        """
        Get a 2D-image for *dataset* for the given variable *name*.
        :param dataset: the dataset returned by :py:meth:`open_dataset`.
        :param name: the variable name.
        :return: a 2D-image
        """

    def transform_source_image(self, source_image):
        """
        Does nothing but returning the source image. Override to implement transformations if needed.
        :param source_image: 2D image
        :return: *source_image*
        """
        return source_image

    def close(self):
        """Does nothing. Override to implement any required close operation."""
        pass


class NetCDFStaticCubeSourceProvider(BaseStaticCubeSourceProvider, metaclass=ABCMeta):
    """
    A CubeSourceProvider that
    * Uses a NetCDF source dataset read from a given **dir_path**
    * Performs only spatial resampling

    :param cube_config: Specifies the fixed layout and conventions used for the cube.
    :param name: The provider's registration name.
    :param dir_path: Source directory to read the single file from. If relative path,
           it will be resolved against the **cube_sources_root** path of the
           global ESDL configuration (**esdl.util.Config.instance()**).
    """

    def __init__(self, cube_config: CubeConfig, name: str, dir_path: str):
        super(NetCDFStaticCubeSourceProvider, self).__init__(cube_config, name)
        if dir_path is None:
            raise ValueError('dir_path expected')
        if not os.path.isabs(dir_path):
            self._dir_path = Config.instance().get_cube_source_path(dir_path)
        else:
            self._dir_path = dir_path
        self.cube_config.static_data = True

    @property
    def dir_path(self):
        return self._dir_path

    def open_dataset(self):
        file_paths = glob.glob(os.path.join(self._dir_path, '*.nc'))
        if not file_paths:
            raise ValueError('No *.nc file found in %s' % self._dir_path)
        file = file_paths[0]
        return netCDF4.Dataset(file)

    def close_dataset(self, dataset):
        dataset.close()

    def get_dataset_file_path(self, dataset):
        return dataset.filepath

    def get_dataset_image(self, dataset, var_name):
        variable = dataset.variables[var_name]
        if len(variable.shape) == 3:
            var_image = variable[0, :, :]
        elif len(variable.shape) == 2:
            var_image = variable[:, :]
        else:
            raise ValueError("unexpected shape for variable '%s'" % var_name)
        return var_image


class DatasetCubeSourceProvider(BaseCubeSourceProvider, Generic[C], metaclass=ABCMeta):
    """
    A BaseCubeSourceProvider that
    * Uses NetCDF source datasets read from a given **dir_path**
    * Performs temporal aggregation first and then spatial resampling
    :param cache: C: Specifies the date cache type to be used. Can be CateDatasetCache or NetCDFDatasetCache
           at this stage
    :param cube_config: Specifies the fixed layout and conventions used for the cube.
    :param name: The provider's registration name.
    :param dir_path: Source directory to read the files from. If relative path,
           it will be resolved against the **cube_sources_root** path of the
           global ESDL configuration (**esdl.util.Config.instance()**).
    :param resampling_order: The order in which resampling is performed. One of 'time_first', 'space_first'.
    """

    def __init__(self, cache: C, cube_config: CubeConfig, name: str, dir_path: str, resampling_order: str):
        super().__init__(cube_config, name)

        if dir_path is None:
            raise ValueError('dir_path expected')

        valid_resampling_order = ('time_first', 'space_first')
        if resampling_order is None:
            resampling_order = valid_resampling_order[0]
        if resampling_order not in valid_resampling_order:
            raise ValueError('resampling_order must be one of %s' % str(valid_resampling_order))

        if not os.path.isabs(dir_path):
            self._dir_path = Config.instance().get_cube_source_path(dir_path)
        else:
            self._dir_path = dir_path
        self._resampling_order = resampling_order
        self._dataset_cache = cache
        self._old_indices = None

    @property
    def dir_path(self) -> str:
        return self._dir_path

    @property
    def dataset_cache(self) -> C:
        return self._dataset_cache

    def compute_variable_images_from_sources(self, index_to_weight):

        new_indices = self.close_unused_open_files(index_to_weight)

        var_descriptors = self.variable_descriptors
        target_var_images = dict()
        for var_name, var_attributes in var_descriptors.items():
            source_var_images = [None] * len(new_indices)
            source_weights = [None] * len(new_indices)
            var_image_index = 0
            for i in new_indices:
                file, time_index = self._get_file_and_time_index(i)
                source_name = var_attributes.get('source_name', var_name)
                var_image = self._dataset_cache.get_dataset_variable(file, source_name, time_index)
                var_image = self.transform_source_image(var_image)

                if self._resampling_order == 'space_first':
                    var_image = gtr.resample_2d(var_image,
                                                self.cube_config.grid_width,
                                                self.cube_config.grid_height,
                                                ds_method=_get_ds_method(var_attributes),
                                                us_method=_get_us_method(var_attributes),
                                                fill_value=var_attributes.get('fill_value', np.nan))
                if var_image.shape[1] / var_image.shape[0] != 2.0:
                    print("Warning: wrong size ratio of image in '%s'. Expected 2, got %f" % (
                        file, var_image.shape[1] / var_image.shape[0]))
                source_var_images[var_image_index] = var_image
                source_weights[var_image_index] = index_to_weight[i]
                var_image_index += 1
            if len(new_indices) > 1:
                # Temporal aggregation
                var_image = aggregate_images(source_var_images, weights=source_weights)
            else:
                # Temporal aggregation not required
                var_image = source_var_images[0]
            # Spatial resampling
            if self._resampling_order == 'time_first':
                var_image = gtr.resample_2d(var_image,
                                            self.cube_config.grid_width,
                                            self.cube_config.grid_height,
                                            ds_method=_get_ds_method(var_attributes),
                                            us_method=_get_us_method(var_attributes),
                                            fill_value=var_attributes.get('fill_value', np.nan))
            target_var_images[var_name] = var_image

        return target_var_images

    def transform_source_image(self, source_image):
        """
        Returns the source image. Override to implement transformations if needed.
        :param source_image: 2D image
        :return: source_image
        """
        return source_image

    def close_unused_open_files(self, index_to_weight):
        """
        Close all datasets that wont be used anymore w.r.t. the given **index_to_weight** dictionary passed to the
        **compute_variable_images_from_sources()** method.
        :param index_to_weight: A dictionary mapping time indexes --> weight values.
        :return: set of time indexes into currently active files w.r.t. the given **index_to_weight** parameter.
        """
        new_indices = set(index_to_weight.keys())
        if self._old_indices:
            unused_indices = self._old_indices - new_indices
            for i in unused_indices:
                file, _ = self._get_file_and_time_index(i)
                self._dataset_cache.close_dataset(file)
        self._old_indices = new_indices
        return new_indices

    def close(self):
        self._dataset_cache.close_all_datasets()


class NetCDFCubeSourceProvider(DatasetCubeSourceProvider[NetCDFDatasetCache], metaclass=ABCMeta):
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
        super().__init__(NetCDFDatasetCache(name), cube_config, name, dir_path, resampling_order)
