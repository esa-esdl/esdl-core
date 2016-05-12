from unittest import TestCase
from datetime import datetime

import numpy

from cablab import BaseCubeSourceProvider, CubeConfig


class BaseImageProviderTest(TestCase):
    def test_properties(self):
        cube_config = CubeConfig()
        provider = MyImageProvider(cube_config, [])
        self.assertEqual('test', provider.name)
        self.assertIs(cube_config, provider.cube_config)

    def test_get_images(self):
        provider = MyImageProvider(CubeConfig(),
                                   [(datetime(2010, 1, 1), datetime(2010, 1, 5)),
                                    (datetime(2010, 1, 5), datetime(2010, 1, 9)),
                                    (datetime(2010, 1, 9), datetime(2010, 1, 13))])

        provider.prepare()

        temporal_coverage = provider.temporal_coverage
        self.assertEqual((datetime(2010, 1, 1), datetime(2010, 1, 13)), temporal_coverage)

        # Requested range is exactly within all source ranges
        provider.compute_variable_images(datetime(2010, 1, 1), datetime(2010, 1, 13))
        self.assertEqual([{0: 1.0, 1: 1.0, 2: 1.0}], provider.trace)

        # Requested range overlaps all source ranges
        provider.trace = []
        provider.compute_variable_images(datetime(2009, 12, 30), datetime(2010, 1, 14))
        self.assertEqual([{0: 1.0, 1: 1.0, 2: 1.0}], provider.trace)

        # Requested range is equal to first source range
        provider.trace = []
        provider.compute_variable_images(datetime(2010, 1, 1), datetime(2010, 1, 5))
        self.assertEqual([{0: 1.0}], provider.trace)

        # Requested range is within first source range and within last source range
        provider.trace = []
        provider.compute_variable_images(datetime(2010, 1, 2), datetime(2010, 1, 10))
        self.assertEqual([{0: 0.375, 1: 1.0, 2: 0.125}], provider.trace)

        # Requested range is sub-range of first source range
        provider.trace = []
        provider.compute_variable_images(datetime(2010, 1, 1, 12), datetime(2010, 1, 4, 12))
        self.assertEqual([{0: 1.0}], provider.trace)

        # Requested range is below first source range
        provider.trace = []
        provider.compute_variable_images(datetime(2009, 1, 2), datetime(2009, 1, 10))
        self.assertEqual([], provider.trace)

        # Requested range is after last source range
        provider.trace = []
        provider.compute_variable_images(datetime(2012, 1, 2), datetime(2012, 1, 10))
        self.assertEqual([], provider.trace)


class MyImageProvider(BaseCubeSourceProvider):
    def __init__(self, cube_config, source_time_ranges):
        super(MyImageProvider, self).__init__(cube_config, 'test')
        self.my_source_time_ranges = source_time_ranges
        self.trace = []
        self.lai_value = 0.1
        self.fapar_value = 0.6

    @property
    def variable_descriptors(self):
        return {
            'LAI': {
                'data_type': numpy.float32,
                'fill_value': 0.0,
                'scale_factor': 1.0,
                'add_offset': 0.0,
            },
            'FAPAR': {
                'data_type': numpy.float32,
                'fill_value': -9999.0,
                'units': '1',
                'long_name': 'FAPAR'
            }
        }

    def compute_source_time_ranges(self):
        return self.my_source_time_ranges

    def compute_variable_images_from_sources(self, index_to_weight):
        self.trace.append(index_to_weight)
        self.lai_value += 0.01
        self.fapar_value += 0.005
        image_width = self.cube_config.grid_width
        image_height = self.cube_config.grid_height
        image_shape = (image_height, image_width)
        return {'LAI': numpy.full(image_shape, self.lai_value, dtype=numpy.float32),
                'FAPAR': numpy.full(image_shape, self.fapar_value, dtype=numpy.float32)}

    def close(self):
        pass
