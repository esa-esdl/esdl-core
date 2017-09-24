import os.path
import shutil
from contextlib import contextmanager
from datetime import datetime
from unittest import TestCase

import xarray as xr

from cablab import Cube, CubeConfig
from cablab.cube_provider import TestCubeSourceProvider

CUBE_DIR = 'testcube'


def _del_cube_dir():
    while os.path.exists(CUBE_DIR):
        shutil.rmtree(CUBE_DIR, False)


class CubeDataAccessTest(TestCase):
    @contextmanager
    def open_access(self):
        """
        Allow to open cube access with a ``with`` statement.
        Note: move this code into Cube later!
        :return: CubeDataAccess instance
        """
        cube = Cube.open(CUBE_DIR)
        data = cube.data
        yield data
        data.close()

    @classmethod
    def setUpClass(cls):
        _del_cube_dir()
        cube = Cube.create(CUBE_DIR, CubeConfig(spatial_res=1.0,
                                                start_time=datetime(2005, 1, 1),
                                                end_time=datetime(2005, 3, 1),
                                                grid_width=360, grid_height=180,
                                                compression=True))
        try:
            cube.update(TestCubeSourceProvider(cube.config, var='a_var'))
            cube.update(TestCubeSourceProvider(cube.config, var='b_var'))
            cube.update(TestCubeSourceProvider(cube.config, var='c_var'))
        finally:
            cube.close()

    @classmethod
    def tearDownClass(cls):
        _del_cube_dir()

    def test_variable_api(self):
        with self.open_access() as data:
            self.assertEquals(['a_var', 'b_var', 'c_var'], data.variable_names)

            var = data.variable('a_var')
            self.assertIs(xr.Variable, type(var))

            vars = data.variable([0, 2, 1])
            self.assertIs(list, type(vars))
            self.assertEqual(3, len(vars))
            self.assertEqual(xr.Variable, type(vars[0]))
            self.assertEqual(xr.Variable, type(vars[1]))
            self.assertEqual(xr.Variable, type(vars[2]))

            vars = data.variable(['a_var', 'c_var'])
            self.assertIs(list, type(vars))
            self.assertEqual(2, len(vars))
            self.assertEqual(xr.Variable, type(vars[0]))
            self.assertEqual(xr.Variable, type(vars[1]))

            vars = data.variable(('a_var', 'c_var',))
            self.assertIs(list, type(vars))
            self.assertEqual(2, len(vars))
            self.assertEqual(xr.Variable, type(vars[0]))
            self.assertEqual(xr.Variable, type(vars[1]))

    def test_get_item_api(self):
        with self.open_access() as data:
            self.assertEqual(3, len(data))

            var = data[0]
            self.assertIs(xr.Variable, type(var))

            var = data['a_var']
            self.assertIs(xr.Variable, type(var))

            vars = data[[0, 2, 1]]
            self.assertIs(list, type(vars))
            self.assertEqual(3, len(vars))
            self.assertEqual(xr.Variable, type(vars[0]))
            self.assertEqual(xr.Variable, type(vars[1]))
            self.assertEqual(xr.Variable, type(vars[2]))

            vars = data[['a_var', 'c_var']]
            self.assertIs(list, type(vars))
            self.assertEqual(2, len(vars))
            self.assertEqual(xr.Variable, type(vars[0]))
            self.assertEqual(xr.Variable, type(vars[1]))

            with self.assertRaises(IndexError):
                # do not allow tuples as index (because data is 1-D, not N-D, with respect to contained variables)
                vars = data['a_var', 'c_var']

    def test_dataset_api(self):
        with self.open_access() as data:
            ds = data.dataset('a_var')
            self.assertIs(xr.Dataset, type(ds))
            self.assertIn('a_var', ds)

            ds = data.dataset(['a_var', 'b_var'])
            self.assertIs(xr.Dataset, type(ds))
            self.assertIn('a_var', ds)
            self.assertIn('b_var', ds)

            ds = data.dataset()
            self.assertIs(xr.Dataset, type(ds))
            self.assertIn('a_var', ds)
            self.assertIn('b_var', ds)
            self.assertIn('c_var', ds)
