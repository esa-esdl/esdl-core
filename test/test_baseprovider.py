from unittest import TestCase
from datetime import datetime

import numpy

from cablab import BaseImageProvider, CubeConfig


class BaseImageProviderTest(TestCase):
    def test_get_images(self):
        config = CubeConfig()
        provider = MyImageProvider([(datetime(2010, 1, 1), datetime(2010, 1, 5)),
                                    (datetime(2010, 1, 5), datetime(2010, 1, 9)),
                                    (datetime(2010, 1, 9), datetime(2010, 1, 13))])

        provider.prepare(config)

        temporal_coverage = provider.get_temporal_coverage()
        self.assertEqual((datetime(2010, 1, 1), datetime(2010, 1, 13)), temporal_coverage)

        # Requested range is exactly within all source ranges
        provider.get_images(datetime(2010, 1, 1), datetime(2010, 1, 13))
        self.assertEqual([{0: 1.0, 1: 1.0, 2: 1.0}], provider.trace)

        # Requested range overlaps all source ranges
        provider.trace = []
        provider.get_images(datetime(2009, 12, 30), datetime(2010, 1, 14))
        self.assertEqual([{0: 1.0, 1: 1.0, 2: 1.0}], provider.trace)

        # Requested range is equal to first source range
        provider.trace = []
        provider.get_images(datetime(2010, 1, 1), datetime(2010, 1, 5))
        self.assertEqual([{0: 1.0}], provider.trace)

        # Requested range is within first source range and within last source range
        provider.trace = []
        provider.get_images(datetime(2010, 1, 2), datetime(2010, 1, 10))
        self.assertEqual([{0: 0.375, 1: 1.0, 2: 0.125}], provider.trace)

        # Requested range is sub-range of first source range
        provider.trace = []
        provider.get_images(datetime(2010, 1, 1, 12), datetime(2010, 1, 4, 12))
        self.assertEqual([{0: 0.75}], provider.trace)

        # Requested range is below first source range
        provider.trace = []
        provider.get_images(datetime(2009, 1, 2), datetime(2009, 1, 10))
        self.assertEqual([], provider.trace)

        # Requested range is after last source range
        provider.trace = []
        provider.get_images(datetime(2012, 1, 2), datetime(2012, 1, 10))
        self.assertEqual([], provider.trace)


class MyImageProvider(BaseImageProvider):
    def __init__(self, source_time_ranges):
        super(MyImageProvider, self).__init__()
        self.source_time_ranges = source_time_ranges
        self.trace = []
        self.lai_value = 0.1
        self.fapar_value = 0.6

    def get_source_time_ranges(self):
        return self.source_time_ranges

    def compute_images_from_sources(self, source_indices_to_time_overlap):
        self.trace.append(source_indices_to_time_overlap)
        self.lai_value += 0.01
        self.fapar_value += 0.005
        image_width = self.cube_config.grid_width
        image_height = self.cube_config.grid_height
        image_shape = (image_height, image_width)
        return {'LAI': numpy.full(image_shape, self.lai_value, dtype=numpy.float32),
                'FAPAR': numpy.full(image_shape, self.fapar_value, dtype=numpy.float32)}

    def prepare(self, cube_config):
        super(MyImageProvider, self).prepare(cube_config)

    def get_variable_metadata(self, variable):
        metadata = {
            'datatype': numpy.float32,
            'fill_value': 0.0,
            'units': '1',
            'long_name': variable,
            'scale_factor': 1.0,
            'add_offset': 0.0,
        }
        return metadata

    def get_spatial_coverage(self):
        return 0, 0, self.cube_config.grid_width, self.cube_config.grid_height

    def close(self):
        pass
