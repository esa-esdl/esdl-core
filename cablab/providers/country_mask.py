import numpy

from cablab import NetCDFStaticCubeSourceProvider


class CountryMaskProvider(NetCDFStaticCubeSourceProvider):
    def __init__(self, cube_config, name='country_mask', dir=None):
        super(CountryMaskProvider, self).__init__(cube_config, name, dir)

    @property
    def variable_descriptors(self):
        return {
            'country_mask': {
                'source_name': 'layer',
                'data_type': numpy.float32,
                'fill_value': -3.4E38,
                'units': '-',
                'standard_name': 'country_mask',
            }
        }
