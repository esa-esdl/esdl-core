from unittest import TestCase
from esdl.cube_store import CubesStore
import os


class TestCubeStoreX(TestCase):

    def test_store_obs(self):
        config = 'https://obs-esdc-configs.obs.eu-de.otc.t-systems.com/datacube_paths.json'
        print(CubesStore(config))
        print("store")

    def test_store_local(self):
        config = os.path.join('.', 'datacube_paths.json')
        print(CubesStore(config))
        print("store")
