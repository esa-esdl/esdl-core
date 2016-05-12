from unittest import TestCase

import cablab.cube_gen


class MainTest(TestCase):
    def test_main(self):
        cablab.cube_gen.main(['--list'])
        # todo (nf 20160512) - fetch stdout and verify
