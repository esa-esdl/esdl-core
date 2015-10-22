from unittest import TestCase
import shutil
from datetime import datetime

from cablab import *
from cablab.cube import _get_cube_times_for_src


class CablabApiTest(TestCase):
    def test_that_api_is_available(self):
        self.assertIsNotNone(CubeConfig)
        self.assertIsNotNone(Cube)

    def test_api_usage(self):
        import os

        base_dir = './testcube'
        if os.path.exists(base_dir):
            shutil.rmtree(base_dir, True)
        self.assertFalse(os.path.exists(base_dir))

        config = CubeConfig()
        cube = Cube.create(config, base_dir)
        self.assertTrue(os.path.exists(base_dir))
        var = cube.add_variable('LAI', MyLaiProvider())
        self.assertTrue(os.path.exists(base_dir + "/LAI"))

        self.assertIs(var, cube.get_variable('LAI'))
        self.assertIs(var, cube.get_variable('LAI'))

    def test_get_cube_times_for_src(self):
        self.assertEqual((datetime(2010, 1, 1),
                          datetime(2010, 1, 9)),
                         _get_cube_times_for_src(datetime(2010, 1, 1),
                                                datetime(2010, 1, 1), 8))
        self.assertEqual((datetime(2010, 1, 1),
                          datetime(2010, 1, 9)),
                         _get_cube_times_for_src(datetime(2010, 1, 2),
                                                datetime(2010, 1, 1), 8))
        self.assertEqual((datetime(2010, 1, 1),
                          datetime(2010, 1, 9)),
                         _get_cube_times_for_src(datetime(2010, 1, 8),
                                                datetime(2010, 1, 1), 8))
        self.assertEqual((datetime(2010, 1, 9),
                          datetime(2010, 1, 17)),
                         _get_cube_times_for_src(datetime(2010, 1, 9),
                                                datetime(2010, 1, 1), 8))
        self.assertEqual((datetime(2010, 1, 9),
                          datetime(2010, 1, 17)),
                         _get_cube_times_for_src(datetime(2010, 1, 12),
                                                datetime(2010, 1, 1), 8))
        self.assertEqual((datetime(2010, 1, 17),
                          datetime(2010, 1, 25)),
                         _get_cube_times_for_src(datetime(2010, 1, 17),
                                                datetime(2010, 1, 1), 8))
        self.assertEqual((datetime(2010, 1, 17),
                          datetime(2010, 1, 25)),
                         _get_cube_times_for_src(datetime(2010, 1, 22),
                                                datetime(2010, 1, 1), 8))


class MyLaiProvider:
    pass
