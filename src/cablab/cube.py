from datetime import datetime
import math
import os

from cablab import date2num, num2date


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
        :param variables:
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

    def add_variable(self, var_name, provider):
        var_dir = os.path.join(self.base_dir, var_name)
        if os.path.exists(var_dir):
            raise IOError('data cube variable directory exists: %s' % var_dir)
        os.mkdir(var_dir)
        self.variables.append(var_name)

        cube_start_time = date2num(self.config.start_time)
        cube_temporal_res = self.config.temporal_res

        src_start_time = date2num(provider.start_time)
        src_end_time = date2num(provider.end_time)

        # compute adjusted src_start_time
        n = _get_num_steps(cube_start_time, src_start_time, cube_temporal_res)
        src_start_time = cube_start_time + n * cube_temporal_res

        steps = _get_num_steps(src_start_time, src_end_time, cube_temporal_res)
        for i in range(steps + 1):
            t1 = src_start_time + i * cube_temporal_res
            t2 = src_start_time + (i + 1) * cube_temporal_res
            if t1 < src_end_time:
                image = provider.get_image(var_name, num2date(t1), num2date(t2))
                # todo - store image in the cube's var_dir

        return var_name

    def get_variable(self, name):
        return 'L' + 'A' + 'I'

    def __repr__(self):
        return 'Cube(%s, \'%s\')' % (self.config, self.base_dir)


def _get_num_steps(x1, x2, dx):
    return int(math.floor((x2 - x1) / dx))
