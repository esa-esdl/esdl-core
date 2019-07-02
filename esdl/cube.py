import math
import os
from datetime import datetime, timedelta

import warnings
import netCDF4
import numpy as np
import esdl
import xarray as xr
import esdl.util
import zarr
from numcodecs import Blosc
from .cube_access import CubeDataAccess
from .cube_config import CubeConfig, CUBE_CHANGELOG
# from .cube_provider import CubeSourceProvider
from .version import version as __version__


class Cube:
    """
    Represents a data cube. Use the static **open()** or **create()** methods to obtain data cube objects.
    """

    def __init__(self, base_dir, config):
        self._base_dir = base_dir
        self._config = config
        self._closed = False
        self._data = None

    def __repr__(self) -> str:
        return 'Cube(%s, \'%s\')' % (self._config, self._base_dir)

    @property
    def base_dir(self) -> str:
        """
        The cube's base directory.
        """
        return self._base_dir

    @property
    def config(self) -> CubeConfig:
        """
        The cube's configuration. See CubeConfig class.
        """
        return self._config

    def info(self) -> str:
        """
        Return a human-readable information string about this data cube (markdown formatted).
        """
        # TODO (forman, 20151104): read from data cube's dir, see issue #5
        return ''

    @property
    def closed(self):
        """
        Checks if the cube has been closed.
        """
        return self._closed

    @property
    def data(self) -> CubeDataAccess:
        """
        The cube's data represented as an xarray dataset
        """
        if not self._data:
            self._data = xr.open_zarr(self.base_dir)
        return self._data

    @staticmethod
    def open(base_dir):
        """
        Open an existing data cube. Use the **Cube.update(provider)** method to add data to the cube
        via a source data provider.

        :param base_dir: The data cube's base directory which must be empty or non-existent.
        :return: A cube instance.
        """

        if not os.path.exists(base_dir):
            raise IOError('data cube base directory does not exists: %s' % base_dir)
        zg = zarr.open_group(base_dir)

        #Construct a CubeConfig object from the zarr attributes.
        #datetime values have to be parsed
        config = zg.attrs['cube.config']
        for k in ('start_time', 'end_time', 'ref_time'):
            dt = datetime.strptime(config[k], '%Y-%m-%d %H:%M:%S')
            config[k] = dt

        CubeConfig._ensure_compatible_config(config)
        return Cube(base_dir, CubeConfig(**config))

    @staticmethod
    def create(base_dir, config=CubeConfig()):
        """
        Create a new data cube. Use the **Cube.update(provider)** method to add data to the cube
        via a source data provider.

        :param base_dir: The data cube's base directory. Must not exists.
        :param config: The data cube's static information.
        :return: A cube instance.
        """

        if os.path.exists(base_dir):
            raise IOError('data cube base directory exists: %s' % base_dir)

        num_periods_per_year = config.num_periods_per_year
        bndsdim = ('bnds', [0, 1])

        temporal_res = config.temporal_res
        start_year = config.start_time.year
        end_year = config.end_time.year
        start_nums = [config.date2num(datetime(yr, 1, 1)) for yr in range(start_year, end_year)]

        time_bnds_attrs = {
            'units': config.time_units,
            'calendar': config.calendar,
            '_ARRAY_DIMENSIONS': ['time', 'bnds']
        }

        def correctub(sn, temporal_res, i, ntot):
            if i == (ntot-1):
                return sn+366
            else:
                return sn + temporal_res * (i + 1.0)

        lower_bounds = [sn + temporal_res * (i + 0.0)
                        for sn in start_nums for i in range(num_periods_per_year)]
        upper_bounds = [correctub(sn, temporal_res, i, num_periods_per_year)
                        for sn in start_nums for i in range(num_periods_per_year)]
        time_bnds_vals = np.zeros((len(lower_bounds), 2))
        time_bnds_vals[:, 0] = lower_bounds
        time_bnds_vals[:, 1] = upper_bounds

        time_attrs = {
            'long_name': 'time',
            'standard_name': 'time',
            'units': config.time_units,
            'calendar': config.calendar,
            'bounds': 'time_bnds',
            '_ARRAY_DIMENSIONS': ['time'],
        }
        time_vals = [sn + temporal_res * (i + 0.5)
                     for sn in start_nums for i in range(num_periods_per_year)]
        # times[-1] = var_time_bnds[-1,0] + (var_time_bnds[-1,1] - var_time_bnds[-1,0]) / 2.
        # Thus, we keep date of the last time range always at Julian day 364, not in the center of the period.
        # The time bounds then specify the real extent of the period.
        # Uncomment the upper line to center it between the upper and lower bound!

        lon_attrs = {
            'long_name': 'longitude',
            'standard_name': 'longitude',
            'units': 'degrees_east',
            'bounds': 'lon_bnds',
            '_ARRAY_DIMENSIONS': ['lon'],
        }
        lon_bnds_attrs = {'units': 'degrees_east', '_ARRAY_DIMENSIONS': ['lon', 'bnds']}

        lat_attrs = {
            'long_name': 'latitude',
            'standard_name': 'latitude',
            'units': 'degrees_north',
            'bounds': 'lat_bnds',
            '_ARRAY_DIMENSIONS': ['lat'],
        }

        lat_bnds_attrs = {'units': 'degrees_north', '_ARRAY_DIMENSIONS': ['lat', 'bnds']}

        lon_vals = np.zeros(config.grid_width)
        lon_bnds_vals = np.zeros((config.grid_width, 2))
        lon_breakpoints = np.linspace(config.lon0, config.lon1, config.grid_width+1, True)
        lon_bnds_vals[:, 0] = lon_breakpoints[0:config.grid_width]
        lon_bnds_vals[:, 1] = lon_breakpoints[1:config.grid_width+1]
        lon_vals            = (lon_bnds_vals[:, 0] + lon_bnds_vals[:, 1])/2

        lat_vals = np.zeros(config.grid_height)
        lat_bnds_vals = np.zeros((config.grid_height, 2))
        lat_breakpoints = np.linspace(config.lat0, config.lat1, config.grid_height+1, True)
        lat_bnds_vals[:, 0] = lat_breakpoints[0:config.grid_height]
        lat_bnds_vals[:, 1] = lat_breakpoints[1:config.grid_height+1]
        lat_vals            = (lat_bnds_vals[:, 0] + lat_bnds_vals[:, 1])/2

        ds = xr.Dataset(coords = {
                         'time': time_vals,
                         'lat' : lat_vals,
                         'lon' : lon_vals,
                         'time_bnds': (['time', 'bnds'], time_bnds_vals),
                         'lat_bnds': (['lat', 'bnds'], lat_bnds_vals),
                         'lon_bnds': (['lon', 'bnds'], lon_bnds_vals),
                         })

        ds.attrs['CHANGELOG'] = CUBE_CHANGELOG

        ds.coords['time'].attrs.update(time_attrs)
        ds.coords['lon'].attrs.update(lon_attrs)
        ds.coords['lat'].attrs.update(lat_attrs)
        ds.coords['time_bnds'].attrs.update(time_bnds_attrs)
        ds.coords['lon_bnds'].attrs.update(lon_bnds_attrs)
        ds.coords['lat_bnds'].attrs.update(lat_bnds_attrs)

        dsz = ds.to_zarr(base_dir)

        #Write the cubeconfig attribute directly to zarr because this is a nested
        #dict and not NetCDF compatible, so xarray won't accept this
        configdict = {}

        # Convert datetimes to string for JSON repr
        for k, v in config.__dict__.items():
            if isinstance(v, datetime):
                configdict[k] = str(v)
            else:
                configdict[k] = v

        z = zarr.open_group(base_dir)
        z.attrs['cube.config'] = configdict

        return Cube(base_dir, config)

    def close(self):
        warnings.warn("This function is deprecated. Zarr cubes do not have to be closed.", DeprecationWarning)

    def update(self, provider: 'CubeSourceProvider', n_imagecache=12):
        """
        Updates the data cube with source data from the given image provider.

        :param provider: An instance of the abstract ImageProvider class
        """
        if self._closed:
            raise IOError('cube has been closed')

        provider.prepare()
        try:
            target_start_time, target_end_time = provider.temporal_coverage
        except Exception as e:
            raise e
        if self._config.start_time and self._config.start_time > target_start_time:
            target_start_time = self._config.start_time
        if self._config.end_time and self._config.end_time < target_end_time:
            target_end_time = self._config.end_time

        dsgroup = zarr.open_group(self.base_dir)

        # Initiate zarr datasets
        for varname in provider.variable_descriptors:
            if not varname in dsgroup.array_keys():
                self._init_variable_dataset(provider, varname)

        varnames = provider.variable_descriptors.keys()
        target_year_1 = target_start_time.year
        target_year_2 = target_end_time.year
        cube_temporal_res = self._config.temporal_res
        num_periods_per_year = self._config.num_periods_per_year
        datasets = {varname: dsgroup[varname] for varname in provider.variable_descriptors}
        imagecache = []

        # Preallocate cache so that multiple images may be written at once,
        # This should be much faster when writing time series

        # Initial index inside zarr array to write to
        i0 = (target_year_1-self._config.start_time.year)*num_periods_per_year
        ilast = i0-1
        for target_year in range(target_year_1, target_year_2+1):
            time_min = datetime(target_year, 1, 1)
            time_max = datetime(target_year + 1, 1, 1)
            d_time = timedelta(days=cube_temporal_res)
            time_1 = time_min
            print(num_periods_per_year)
            for time_index in range(num_periods_per_year):
                time_2 = time_1 + d_time
                if time_2 > time_max:
                    time_2 = time_max
                weight = esdl.util.temporal_weight(
                    time_1, time_2, target_start_time, target_end_time)
                if weight > 0.0:
                    var_name_to_image = provider.compute_variable_images(time_1, time_2)
                    if var_name_to_image:
                        imagecache.append((i0, var_name_to_image))
                print("t1: ", time_1, " t2: ", time_2)
                if i0-ilast >= n_imagecache:
                    print("i0 ilast", i0, ilast)
                    if len(imagecache) > 0:
                        print(datasets)
                        self._write_images(provider, datasets, imagecache, varnames, n_imagecache)
                    imagecache = []
                    ilast = i0
                time_1 = time_2
                i0 = i0 + 1
        if len(imagecache) > 0:
            self._write_images(provider, datasets, imagecache, varnames, n_imagecache)
        provider.close()

    def _write_images(self, provider, datasets, imagecache, varnames, n_imagecache):
        # First we unpack the data into 3d-numpy arrays
        for var_name in varnames:
            ds = datasets[var_name]
            i0 = imagecache[0][0]
            iend = imagecache[-1][0] + 1
            im_first = imagecache[0][1][var_name]
            image_all = np.full(
                (iend-i0, im_first.shape[0], im_first.shape[1]), ds.fill_value, ds.dtype)
            for entry in imagecache:
                i1 = entry[0]
                im_now = entry[1][var_name]
                image_all[i1-i0, :, :] = im_now
            print("Writing variable %s image from time index %d to %d" % (var_name, i0, iend))
            ds[i0:iend, :, :] = image_all

    def _init_variable_dataset(self, provider, variable_name):
        import time

        zdataset = zarr.open_group(self.base_dir)

        nt = len(zdataset['time'])
        nx = len(zdataset['lon'])
        ny = len(zdataset['lat'])

        if not self._config.chunk_sizes:
            cs = (1, ny, nx)
        else:
            cs = self._config.chunk_sizes

        if self._config.compression:
            compressor = Blosc(cname='lz4', clevel=self._config.comp_level)
        else:
            compressor = None

        variable_descriptors = provider.variable_descriptors
        variable_attributes = variable_descriptors[variable_name]

        newds = zdataset.create_dataset(variable_name, shape=(nt, ny, nx), chunks=cs,
                                        dtype=variable_attributes['data_type'], compressor=compressor,
                                        fillvalue=variable_attributes['fill_value'])

        # TODO (forman, 20160512): some of these attributes could be read from cube configuration
        # see http://cfconventions.org/cf-conventions/v1.6.0/cf-conventions.html#description-of-file-contents
        # see http://cfconventions.org/cf-conventions/v1.6.0/cf-conventions.html#attribute-appendix
        #
        # check (nf 20151023) - add more global attributes from CF-conventions here,
        #                       especially those that reference original sources and originators
        #
        # dataset.title = ...
        # dataset.references = ...
        # dataset.comment = ...
        source_attributes = {k: v for k, v in variable_attributes.items(
        ) if k not in {'data_type', 'fill_value', 'scale_factor', 'add_offset'}}
        all_attributes = {
            'Conventions': 'CF-1.6',
            'institution': 'Brockmann Consult GmbH, Germany',
            'source':  'ESDL data cube generation, version %s' % __version__,
            'history': time.ctime(time.time()) + ' - ESDL data cube generation',
            'northing': '%s degrees' % self.config.northing,
            'easting': '%s degrees' % self.config.easting,
            'source_attributes': source_attributes,
            # This is actually mangling with xarray-internals to tell xarray about the dimension variables
            # This will have to change in the future, once there is something like a NetZDF zarr extension
            # defined, see e.g. issue
            '_ARRAY_DIMENSIONS': ["time", "lat", "lon"]
        }
        for k in all_attributes:
            newds.attrs[k] = all_attributes[k]

        return newds

    @staticmethod
    def _get_num_steps(x1, x2, dx):
        return int(math.floor((x2 - x1) / dx))
