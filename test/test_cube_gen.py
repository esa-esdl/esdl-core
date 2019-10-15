import os
from collections import OrderedDict
from unittest import TestCase

from esdl.cube_gen import _parse_source_arg
from esdl.cube_gen import main


class MainTest(TestCase):
    def test_list_mode(self):
        main(['--list'])
        # todo (nf 20160512) - fetch stdout and verify

    def test_parse_source_arg(self):
        self.assertEqual(('', None, None, 'SOURCE name must not be empty'), _parse_source_arg(''))
        self.assertEqual(('', None, None, 'SOURCE name must not be empty'),
                         _parse_source_arg(os.pathsep))
        self.assertEqual(('', None, None, 'SOURCE name must not be empty'),
                         _parse_source_arg(os.pathsep + 'a'))
        self.assertEqual(('a', [['']], OrderedDict(), None), _parse_source_arg('a' + os.pathsep))
        self.assertEqual(('a', [['b']], OrderedDict(), None),
                         _parse_source_arg('a' + os.pathsep + 'b'))
        self.assertEqual(('a', [['b']], OrderedDict([('c', '8')]), None),
                         _parse_source_arg('a' + os.pathsep + 'b' + os.pathsep + 'c=8'))
        self.assertEqual(('a', [['c'], ['e']], OrderedDict([('b', '1'), ('d', '2')]), None),
                         _parse_source_arg(
            'a' + os.pathsep + 'b=1' + os.pathsep + 'c' + os.pathsep + 'd=2' + os.pathsep + 'e'))
