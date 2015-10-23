from unittest import TestCase
import shutil

from cablab import CubeConfig, Cube
import cablab.providers.BurntAreaProvider as BurntAreaProvider

import os


class BurntAreaProviderTest(TestCase):
    def test_burnt_area_provider(self):
        base_dir = 'testcube'
        if os.path.exists(base_dir):
            shutil.rmtree(base_dir, True)
        self.assertFalse(os.path.exists(base_dir))

        config = CubeConfig()
        cube = Cube.create(config, base_dir)
        self.assertTrue(os.path.exists(base_dir))

        provider = BurntAreaProvider()
        cube.update(provider)

