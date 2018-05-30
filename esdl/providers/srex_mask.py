import numpy as np

from esdl.cube_provider import NetCDFStaticCubeSourceProvider


class SrexMaskProvider(NetCDFStaticCubeSourceProvider):
    def __init__(self, cube_config, name='srex_mask', dir=None):
        super(SrexMaskProvider, self).__init__(cube_config, name, dir)

    @property
    def variable_descriptors(self):
        return {
            'srex_mask': {
                'source_name': 'layer',
                'data_type': np.float32,
                'fill_value': -3.4E38,
                'units': '-',
                'ds_method': 'MODE',
                'standard_name': 'srex_mask',
                'long_name': 'Mask for SREX regions',
            }
        }
