from datetime import datetime
import math
import os
from abc import ABCMeta, abstractmethod

import numpy

import cablab


class ImageProvider(metaclass=ABCMeta):
    """
    Represents an abstract image provider to be used by the Cube's update() method.
    Intended to be used as base class for specific image provider implementations.
    """

    @abstractmethod
    def prepare(self, cube_config):
        """
        Called by a Cube instance's update() method before any other provider methods are called.
        Provider instances should prepare themselves w.r.t. the given cube configuration.
        :param cube_config: The data cube config, instance of CubeConfig
        """
        pass

    @abstractmethod
    def get_temporal_coverage(self):
        """
        Return the start and end time of the available source data.
        :return: A tuple of datetime.datetime instances (start_time, end_time).
        """
        return None

    @abstractmethod
    def get_spatial_coverage(self):
        """
        Return the spatial coverage as a rectangle represented by a tuple (x, y, width, height) in the cube's image
        coordinates.
        :return: A tuple of integers (x, y, width, height) in the cube's image coordinates.
        """
        return None

    @abstractmethod
    def get_images(self, image_start_time, image_end_time):
        """
        Return a dictionary of variable names to image mappings where each image is a numpy array with the the shape
        (height, width) derived from the get_spatial_coverage() method. The images must be computed (by aggregation
        or interpolation) from the source data in the temporal range image_start_time <= source_data_time
        < image_end_time and taking into account other data cube configuration settings.
        Called by a Cube instance's update() method for all possible time periods in the time range given by the
        get_temporal_coverage() method. The times given are adjusted w.r.t. the cube's start time and temporal
        resolution.

        :param: image_start_time The image start time as a datetime.datetime instance
        :param: image_end_time The image end time as a datetime.datetime instance
        :return: A dictionary variable_name --> image (numpy array of size (width, height)) or None if no such
        variables exists for the given time range.
        """
        return None

    @abstractmethod
    def close(self):
        """
        Called by the cube's update() method after all images have been retrieved and the provider is no longer used.
        """
        pass


class CubeConfig:
    """
    A data cube's static configuration information.

    >>> CubeConfig(2880, 1440)
    CubeConfig(2880, 1440, -180.0, -90.0, 0.25)
    """

    def __init__(self,
                 grid_width=1440,
                 grid_height=720,
                 easting=-180.0,
                 northing=-90.0,
                 spatial_res=0.25,
                 start_time=datetime(2000, 1, 1),
                 temporal_res=8,
                 variables=None):
        """
        Create a configuration to be be used for creating new data cubes.

        :param grid_width: The fixed image width in pixels (longitude direction)
        :param grid_height: The fixed image height in pixels (latitude direction)
        :param easting: The longitude position of the lower-left-most corner of the lower-left-most image pixel
        :param northing: The latitude position of the lower-left-most corner of the lower-left-most image pixel
        :param spatial_res: The spatial image resolution in degree
        :param start_time: The start time of the first image
        :param temporal_res: The temporal resolution in days
        :param variables: A list of variable names to be included in the cube.
        :return: the new configuration
        """

        self.grid_width = grid_width
        self.grid_height = grid_height
        self.easting = easting
        self.northing = northing
        self.spatial_res = spatial_res
        self.start_time = start_time
        self.temporal_res = temporal_res
        self.variables = variables

    def __repr__(self):
        return 'CubeConfig(%s, %s, %s, %s, %s)' % (
            self.grid_width, self.grid_height,
            self.easting, self.northing, self.spatial_res)


class Cube:
    """
    Represents an existing data cube.

    >>> Cube.create(CubeConfig(), '/home/hans/mycube')
    Cube(CubeConfig(1440, 720, -180.0, -90.0, 0.25), '/home/hans/mycube')
    """

    def __init__(self, config, base_dir):
        self.config = config
        self.base_dir = base_dir
        self.variables = []

    @staticmethod
    def create(config, base_dir):

        if os.path.exists(base_dir):
            raise IOError('data cube base directory exists: %s' % base_dir)
        os.mkdir(base_dir)
        return Cube(config, base_dir)

    def update(self, provider):

        provider.prepare(self.config)

        cube_start_time = cablab.date2num(self.config.start_time)
        cube_temporal_res = self.config.temporal_res

        src_start_time, src_end_time = provider.get_temporal_coverage()
        src_start_time = cablab.date2num(src_start_time)
        src_end_time = cablab.date2num(src_end_time)

        # compute adjusted src_start_time
        n = _get_num_steps(cube_start_time, src_start_time, cube_temporal_res)
        src_start_time = cube_start_time + n * cube_temporal_res

        steps = _get_num_steps(src_start_time, src_end_time, cube_temporal_res)
        for i in range(steps + 1):
            t1 = src_start_time + i * cube_temporal_res
            t2 = src_start_time + (i + 1) * cube_temporal_res
            if t1 < src_end_time:
                image_dict = provider.get_images(cablab.num2date(t1), cablab.num2date(t2))
                if image_dict:
                    self._write_images(cablab.num2date(t1), cablab.num2date(t2), image_dict)

        provider.close()

    def get_variable(self, name):
        return 'L' + 'A' + 'I'

    def __repr__(self):
        return 'Cube(%s, \'%s\')' % (self.config, self.base_dir)

    def _write_images(self, image_start_time, image_end_time, image_dict):
        for var_name in image_dict:
            image = image_dict[var_name]
            if image is not None:
                var_dir = os.path.join(self.base_dir, var_name)
                if not os.path.exists(var_dir):
                    os.mkdir(var_dir)
                filename = '%s_%s_%s' % (var_name,
                                         str(image_start_time).replace(':', '-').replace(' ', '_'),
                                         str(image_end_time).replace(':', '-').replace(' ', '_'))
                numpy.save(os.path.join(var_dir, filename), image)


def _get_num_steps(x1, x2, dx):
    return int(math.floor((x2 - x1) / dx))
