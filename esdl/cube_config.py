import math
from datetime import datetime
from typing import Tuple

import netCDF4

#: The current version of the data cube's configuration and data model.
#: The model version is incremented on every change of the cube's data model.
CUBE_MODEL_VERSION = '2.0.2'

CUBE_CHANGELOG = """
version 2.0.2
---------------
* added new parameter to cube_config: lon0, lat0, lon1, lat1 to specify upper left corner of
the upper left grid cell and the lower right corner of the lower right grid cell.


version 2.0.1
---------------
* Switched to zarr data format


version 1.0.2
-------------
* Introduced new configuration parameter comp_level (0...9, default 5)

version 1.0.1
-------------
* Configuration parameter chunk_size now used

version 1.0.0
-------------
* First official release to public

version 0.2.4
-------------
* Changed the data type of Ozone from double to float https://github.com/CAB-LAB/cablab-core/issues/54
* Fixed the inconsistencies on the values on the first time step of the second year onwards of the MPI data https://github.com/CAB-LAB/cablab-core/issues/55
* Fixed flipped aerosols data https://github.com/CAB-LAB/cablab-core/issues/57

version 0.2.3
-------------
* Fixed flipped and shifted issue in ozone data https://github.com/CAB-LAB/cablab-core/issues/52
* Fixed the missing value issue in ozone data https://github.com/CAB-LAB/cablab-core/issues/51

version 0.2.2
-------------
* Fixed lon- and pixel- shifted issues in air temperature data
* Changed the downsampling method for country mask variable to MODE

version 0.2.1
-------------
* Remove add_offset and scale_factor from cube data: https://github.com/CAB-LAB/cablab-core/issues/43

version 0.2
-----------
The netCDF file schema has been updated according to the following issues:
* CF-compliant time information: https://github.com/CAB-LAB/cablab-core/issues/30
* CF-compliant variable names (ongoing): https://github.com/CAB-LAB/cablab-core/issues/32
* CF-compliant geospatial information: https://github.com/CAB-LAB/cablab-core/issues/35

version 0.1
-----------
* initial version
"""


class CubeConfig:
    """
    A data cube's static configuration information.

    :param spatial_res: The spatial image resolution in degree.
    :param lon0: Left border of the most left grid cell
    :param lon1: Right border of the most right grid cell
    :param lat0: Upper border of the uppermost grid cell
    :param lat1: Lower border of the lowermost grid cell
    :param grid_width: The fixed grid width in pixels (longitude direction).
    :param grid_height: The fixed grid height in pixels (latitude direction).
    :param temporal_res: The temporal resolution in days.
    :param ref_time: A datetime value which defines the units in which time values are given, namely
                     'days since *ref_time*'.
    :param start_time: The inclusive start time of the first image of any variable in the cube given as datetime value.
                       ``None`` means unlimited.
    :param end_time: The exclusive end time of the last image of any variable in the cube given as datetime value.
                     ``None`` means unlimited.
    :param variables: A list of variable names to be included in the cube.
    :param file_format: The file format used. Must be one of 'NETCDF4', 'NETCDF4_CLASSIC', 'NETCDF3_CLASSIC'
                        or 'NETCDF3_64BIT'.
    :param chunk_sizes: A mapping of dimension names to chunk size for encoding.
                        Default is None.
    :param compression: Whether gzip compression is used for encoding.
                        Default is False.
    :param comp_level: Integer between 1 and 9 describing the level of compression desired for encoding.
                       Default is 5. Ignored if *compression* is False.
    """

    def __init__(self,
                 spatial_res=0.25,
                 grid_x0=0,
                 grid_y0=0,
                 lon0 = None,
                 lon1 = None,
                 lat0 = None,
                 lat1 = None,
                 grid_width=1440,
                 grid_height=720,
                 temporal_res=8,
                 calendar='gregorian',
                 ref_time=datetime(2001, 1, 1),
                 start_time=datetime(2001, 1, 1),
                 end_time=datetime(2012, 1, 1),
                 variables=None,
                 file_format='NETCDF4_CLASSIC',
                 chunk_sizes=None,
                 compression=False,
                 comp_level=5,
                 static_data=False,
                 model_version=CUBE_MODEL_VERSION):
        self.model_version = model_version
        if  (not lon0) | (not lon1) | (not lat0) | (not lat1):
            lon0 = -180 + grid_x0 * spatial_res
            lat0 = 90 - grid_y0 * spatial_res
            lon1 = -180 + (grid_x0 + grid_width) * spatial_res
            lat1 = 90 - (grid_y0 + grid_height) * spatial_res
        self.lon0 = lon0
        self.lon1 = lon1
        self.lat0 = lat0
        self.lat1 = lat1
        self.grid_width = grid_width
        self.grid_height = grid_height
        self.temporal_res = temporal_res
        self.calendar = calendar
        self.ref_time = ref_time
        self.start_time = start_time
        self.end_time = end_time
        self.variables = variables
        self.file_format = file_format
        self.static_data = static_data
        self.chunk_sizes = chunk_sizes
        self.compression = compression
        self.comp_level = comp_level
        self._validate()

    def __repr__(self):
        return 'CubeConfig(grid_width=%d, grid_height=%d, ' \
               'temporal_res=%d, ref_time=%s)' % (
                   self.grid_width, self.grid_height,
                   self.temporal_res,
                   repr(self.ref_time))

    @property
    def northing(self) -> float:
        """
        The longitude position of the upper-left-most corner of the upper-left-most grid cell
        given by (grid_x0, grid_y0).
        """
        return self.lat0

    @property
    def easting(self) -> float:
        """
        The latitude position of the upper-left-most corner of the upper-left-most grid cell
        given by (grid_x0, grid_y0).
        """
        return self.lon0

    @property
    def geo_bounds(self) -> Tuple[Tuple[float, float], Tuple[float, float]]:
        """
        The geographical boundary given as ((LL-lon, LL-lat), (UR-lon, UR-lat)).
        """
        return ((self.grid_lon0, self.grid_lat1),
                (self.grid_lon1, self.grid_lat0))

    @property
    def time_units(self) -> str:
        """
        Return the time units used by the data cube as string using the format 'days since *ref_time*'.
        """
        ref_time = self.ref_time
        return 'days since %4d-%02d-%02d %02d:%02d' % \
               (ref_time.year, ref_time.month, ref_time.day, ref_time.hour, ref_time.minute)

    @property
    def num_periods_per_year(self) -> float:
        """
        Return the integer number of target periods per year.
        """
        return math.ceil(365.0 / self.temporal_res)

    def date2num(self, date) -> float:
        """
        Return the number of days for the given *date* as a number in the time units
        given by the ``time_units`` property.

        :param date: The date as a datetime.datetime value
        """
        return netCDF4.date2num(date, self.time_units, calendar=self.calendar)

    @staticmethod
    def load(path) -> object:
        """
        Load a CubeConfig from a text file.

        :param path: The file's path name.
        :return: A new CubeConfig instance
        """
        config = dict()
        with open(path) as fp:
            code = fp.read()
            exec(code, {'datetime': __import__('datetime')}, config)

        CubeConfig._ensure_compatible_config(config)

        return CubeConfig(**config)

    @staticmethod
    def _ensure_compatible_config(config_dict):
        model_version = config_dict.get('model_version', None)
        # Here: check for compatibility with Cube.MODEL_VERSION, convert if possible, otherwise raise error.
        if model_version is None or model_version < CUBE_MODEL_VERSION:
            print('WARNING: outdated cube model version, current version is %s' % CUBE_MODEL_VERSION)


    def _validate(self):

        lat1 = self.lat1
        lat2 = self.lat0
        if lat1 >= lat2 or lat1 < -90 or lat1 > 90 or lat2 < -90 or lat2 > 90:
            raise ValueError('illegal combination of grid_y0, grid_height, spatial_res values')

        lon1 = self.lon0
        lon2 = self.lon1
        if lon1 >= lon2 or lon1 < -180 or lon1 > 180 or lon2 < -180 or lon2 > 180:
            raise ValueError('illegal combination of grid_x0, grid_width, spatial_res values')

        if self.chunk_sizes is not None and len(self.chunk_sizes) != 3:
            raise ValueError('chunk_sizes must be a sequence of three integers: <time-size>, <lat-size>, <lon-size>')

        if self.comp_level is not None and (self.comp_level < 1 or self.comp_level > 9):
            raise ValueError('comp_level must be an integer in the range 1 to 9')
