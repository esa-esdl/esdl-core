from unittest import TestCase

from cablab import Cube
from cablab.cube_access import CubeDataAccess

CUBE_DIR = 'C:\\Users\\Norman\\EOData\\CAB-LAB\\cube-1.01'


class CubeDataAccessTest(TestCase):
    def test_it(self):
        cube = Cube.open(CUBE_DIR)

        data = CubeDataAccess(cube)

        names = data.variable_names
        print(names)

        ozone_da = data.variables('Ozone')
        ozone_ds = data.dataset('Ozone')
        ozone_precip_ds = data.dataset(['Ozone', 'Precip'])
        #all_ds = data.dataset()

        #self.assertEqual(cube.config.spatial_res, cube2.config.spatial_res)
        #self.assertEqual(cube.config.temporal_res, cube2.config.temporal_res)
        #self.assertEqual(cube.config.file_format, cube2.config.file_format)
        #self.assertEqual(cube.config.compression, cube2.config.compression)

        data.close()
