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

    def add_variable(self, name, provider):
        var_dir = os.path.join(self.base_dir, name)
        if os.path.exists(var_dir):
            raise IOError('data cube variable directory exists: %s' % var_dir)
        os.mkdir(var_dir)
        self.variables.append(name)
        import math
        n = math.floor((date2num(provider.end_time) - date2num(provider.start_time)) / self.config.temporal_res)
        pet = provider.end_time

        cstr = _get_cube_times_for_src(pst, self.config.start_time, self.config.temporal_res)
        cetr = _get_cube_times_for_src(pet, self.config.start_time, self.config.temporal_res)


        cst = cstr[0]
        cet = cetr[0]

        # datasets = sorted(provider.get_datasets(name))
        # for dataset in datasets:
        #    timestamp = dataset.timestamp


        # times_count =
        # [config.start_time + i * timedelta(days=config.temporal_res) for i in range(times_count)]

        return name

    def get_variable(self, name):
        return 'L' + 'A' + 'I'

    def __repr__(self):
        return 'Cube(%s, \'%s\')' % (self.config, self.base_dir)


def _get_cube_times_for_src(src_time, cube_start_time, cube_temporal_res):
    st = date2num(src_time)
    cst = date2num(cube_start_time)
    delta = st - cst
    n = math.floor(delta / cube_temporal_res)
    return num2date(cst + n * cube_temporal_res), num2date(cst + (n + 1) * cube_temporal_res)
