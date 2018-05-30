import numpy

from esdl.cube_provider import NetCDFStaticCubeSourceProvider


class CountryMaskProvider(NetCDFStaticCubeSourceProvider):
    def __init__(self, cube_config, name='country_mask', dir=None):
        super(CountryMaskProvider, self).__init__(cube_config, name, dir)

    @property
    def variable_descriptors(self):
        return {
            'country_mask': {
                'source_name': 'country_mask',
                'data_type': numpy.int32,
                'fill_value': -99,
                'ds_method': 'MODE',
                'units': '-',
                'standard_name': 'country_mask',
            }
        }
