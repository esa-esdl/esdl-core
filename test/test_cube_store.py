import os
import unittest
from unittest import TestCase
from esdl.cube_store import CubesStore

json_str = """
{
  "CUBE_V2.0.0_global_spatially_optimized_0.25deg": {
      "description": "Global data cube at a spatial resolution of 0.25 degrees and a temporal resolution of 8 days with a 1x720x1440 (time x lat x lon) chunking",
      "FileSystem": "obs",
      "Endpoint": "https://obs.eu-de.otc.t-systems.com",
      "Region": "eu-de",
      "Path": "obs-esdc-v2.0.0/esdc-8d-0.25deg-1x720x1440-2.0.0.zarr"
  },
  "CUBE_V2.0.0_global_time_optimized_0.25deg": {
      "description": "Global data cube at a spatial resolution of 0.25 degrees and a temporal resolution of 8 days with a 184x90x90 (time x lat x lon) chunking",
      "FileSystem": "obs",
      "Endpoint": "https://obs.eu-de.otc.t-systems.com",
      "Region": "eu-de",
      "Path": "obs-esdc-v2.0.0/esdc-8d-0.25deg-184x90x90-2.0.0.zarr"
  }
}
"""


class TestCubeStoreX(TestCase):

    @unittest.skip('travis cannot connect to the OTC OBS')
    def test_store_obs(self):
        config = 'https://obs-esdc-configs.obs.eu-de.otc.t-systems.com/datacube_paths.json'
        print(CubesStore(config))
        print("store")

    def test_config_fails(self):
        config = 'test2.json'

        with self.assertRaises(FileNotFoundError) as cm:
            CubesStore(config)
        self.assertEqual('Cannot open test2.json.', f'{cm.exception}')

    def test_store_local(self):
        config = os.path.join('.', 'test.json')
        with open(config, 'w') as json_file:
            json_file.write(json_str)
            json_file.close()

        cs = CubesStore(config)
        expected = {
            "description": "Global data cube at a spatial resolution of 0.25 degrees and a temporal resolution of 8 "
                           "days with a 1x720x1440 (time x lat x lon) chunking",
            "FileSystem": "obs",
            "Endpoint": "https://obs.eu-de.otc.t-systems.com",
            "Region": "eu-de",
            "Path": "obs-esdc-v2.0.0/esdc-8d-0.25deg-1x720x1440-2.0.0.zarr"
        }

        ds = cs._cube_config['CUBE_V2.0.0_global_spatially_optimized_0.25deg']

        self.assertEqual(ds, expected)
        os.remove(config)
