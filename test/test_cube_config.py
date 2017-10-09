from unittest import TestCase

from ..cablab import CubeConfig, CUBE_MODEL_VERSION


class CubeConfigTest(TestCase):
    def test_validate(self):
        with self.assertRaises(ValueError):
            CubeConfig(grid_x0=1)
        with self.assertRaises(ValueError):
            CubeConfig(grid_y0=1)
        with self.assertRaises(ValueError):
            CubeConfig(grid_x0=-1)
        with self.assertRaises(ValueError):
            CubeConfig(grid_y0=-1)

    def test_model_version_is_current(self):
        config = CubeConfig()
        self.assertEqual(CUBE_MODEL_VERSION, config.model_version)

    def test_properties(self):
        config = CubeConfig()

        self.assertEqual(-180, config.easting)
        self.assertEqual(90, config.northing)
        self.assertEqual(((-180, -90), (180, 90)), config.geo_bounds)

        config = CubeConfig(grid_x0=430, grid_y0=28, grid_width=100, grid_height=100, spatial_res=0.5)
        self.assertEqual(35.0, config.easting)
        self.assertEqual(76.0, config.northing)
        self.assertEqual(((35.0, 26.0), (85.0, 76.0)), config.geo_bounds)
