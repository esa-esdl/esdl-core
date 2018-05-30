import numpy as np
from esdl.cube_provider import CubeSourceProvider
from esdl.cube_config import CubeConfig


class TestCubeSourceProvider(CubeSourceProvider):
    """
    CubeSourceProvider implementation used for testing cube generation without any source files.

    The following usage generates a cube with two variables ``test_1`` and ``test_2``:
        cube-gen -c ./myconf.py ./mycube test:var=test_1 test:var=test_2

    :param cube_config: Specifies the fixed layout and conventions used for the cube.
    :param name: The provider's registration name. Defaults to ``"test"``.
    :param var: Name of a (float32) variable which will be filled with random numbers.
    """

    def __init__(self, cube_config: CubeConfig, name: str = 'test', var: str = 'test'):
        super(TestCubeSourceProvider, self).__init__(cube_config, name)
        self._variable_name = var
        self._value = 0.0

    def prepare(self):
        pass

    @property
    def temporal_coverage(self):
        return self.cube_config.start_time, self.cube_config.end_time

    @property
    def spatial_coverage(self):
        return 0, 0, self.cube_config.grid_width, self.cube_config.grid_height

    @property
    def variable_descriptors(self):
        return {
            self._variable_name: {
                'data_type': np.float32,
                'fill_value': np.nan,
                'scale_factor': 1.0,
                'add_offset': 0.0,
            }
        }

    def compute_variable_images(self, period_start, period_end):
        self._value += 0.1
        image_width = self.cube_config.grid_width
        image_height = self.cube_config.grid_height
        image_shape = (image_height, image_width)
        return {
            self._variable_name: np.full(image_shape, self._value, dtype=np.float32)
        }

    def close(self):
        pass
