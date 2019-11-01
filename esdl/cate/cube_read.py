import os.path
import warnings
from collections import OrderedDict
from typing import Optional, Any, Sequence

import xarray as xr
from cate.conf import conf
from cate.core import DataStore, DataSource
from cate.core.ds import DATA_STORE_REGISTRY
from cate.core.op import op, op_input
from cate.core.types import TimeRangeLike, PolygonLike, VarNamesLike, TimeRange
from cate.util.monitor import Monitor

import esdl

__author__ = "Norman Fomferra, Brockmann Consult GmbH"


@op(version='1.0')
@op_input('cube_config_file',
          file_open_mode='r',
          file_filters=[dict(name='ESDC Cube Configuration', extensions=['config'])])
def read_esdc(cube_config_file: str) -> xr.Dataset:
    """
    Read an Earth System Data Cube (ESDC) in the local file system.
    :param cube_config_file: The ESDC configuration file contained within
           a data cube base directory.
    :return: A dataset comprising all the data cube variables.
    """
    cube_base_dir = os.path.dirname(cube_config_file)
    return esdl.Cube.open(cube_base_dir).data.dataset()


class EsdcDataSource(DataSource):
    """
    An ESDC data source represent an individual data cube.
    """

    def __init__(self, data_store: 'EsdcDataStore', ds_id: str, title: str, cube: esdl.Cube):
        self._data_store = data_store
        self._ds_id = ds_id
        self._title = title
        self._cube = cube

    @property
    def data_store(self) -> 'EsdcDataStore':
        return self._data_store

    @property
    def id(self) -> str:
        return self._ds_id

    @property
    def meta_info(self) -> Optional[dict]:
        metadata = dict()
        for key, value in self._cube.config.__dict__.items():
            if not key.startswith('_') and not key.endswith('_'):
                metadata[key] = str(value)
        if self._title:
            metadata['title'] = self._title
        # TODO (forman): get variables from cube, must be list of dict(name=, unit=)
        metadata['variables'] = [dict(name=name) for name in self._cube.data.variable_names]
        return metadata

    def temporal_coverage(self, monitor: Monitor = Monitor.NONE) -> Optional[TimeRange]:
        start_time = self._cube.config.start_time
        end_time = self._cube.config.end_time
        if start_time and end_time:
            try:
                return TimeRangeLike.convert("{},{}".format(start_time, end_time))
            except ValueError:
                pass
        return None

    def open_dataset(self,
                     time_range: TimeRangeLike.TYPE = None,
                     region: PolygonLike.TYPE = None,
                     var_names: VarNamesLike.TYPE = None,
                     protocol: str = None,
                     monitor: Monitor = Monitor.NONE) -> Any:
        if time_range or region or var_names:
            raise ValueError("ESDC data sources cannot have constraints")
        return self._cube.data.dataset()

    def make_local(self, *args, **kwargs) -> Optional[DataSource]:
        warnings.warn('ESDC data sources cannot be made local')
        return None

    def _repr_html_(self):
        # TODO (forman): implement me
        return self.__repr__()


class EsdcDataStore(DataStore):
    """
    A Cate data store implementation exposing each configured ESDC as an individual data source.
    ESDC are configured in Cate's configuration file ``$HOME/.cate/<version>/conf.py`` as follows:::
         esdc_data_sources = [
             (id, title, data_cube_dir_path),
             ...
         ]
    The ``esdc_data_sources``entries are 3-element tuples as follows:
    * *id* is a string that should by prefixed by "esdc.";
    * *title* should be a non-empty, human-readable text;
    * *data_cube_dir_path* is a string pointing to aESDC directory in your local file system.
    """

    def __init__(self):
        super().__init__('esdc', title='Earth System Data Cube', is_local=True)
        esdc_data_source_defs = conf.get_config_value('esdc_data_sources', [])
        self._data_sources = OrderedDict()
        for ds_id, title, local_path in esdc_data_source_defs:
            if not ds_id.startswith('esdc.'):
                ds_id = 'esdc.' + ds_id
            cube = None
            try:
                cube = esdl.Cube.open(local_path)
            except Exception as e:
                warnings.warn('Failed registering ESDC data source "%s": %s' % (ds_id, e))
                pass
            if cube:
                self._data_sources[ds_id] = EsdcDataSource(self, ds_id, title, cube)

    def query(self,
              ds_id: str = None,
              query_expr: str = None,
              monitor: Monitor = Monitor.NONE) -> Sequence[DataSource]:
        if ds_id:
            data_source = self._data_sources.get(ds_id)
            return [data_source] if data_source else []
        # TODO (forman): use query_expr
        return list(self._data_sources.values())

    def _repr_html_(self):
        # TODO (forman): implement me
        return self.__repr__()


def cate_init():
    DATA_STORE_REGISTRY.add_data_store(EsdcDataStore())