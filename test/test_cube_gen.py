from collections import OrderedDict
from unittest import TestCase

from cablab.cube_gen import _parse_source_arg
from cablab.cube_gen import main


class MainTest(TestCase):
    def test_list_mode(self):
        main(['--list'])
        # todo (nf 20160512) - fetch stdout and verify

    def test_parse_source_arg(self):
        self.assertEquals(('', None, None, 'SOURCE name must not be empty'), _parse_source_arg(''))
        self.assertEquals(('', None, None, 'SOURCE name must not be empty'), _parse_source_arg(':'))
        self.assertEquals(('', None, None, 'SOURCE name must not be empty'), _parse_source_arg(':a'))
        self.assertEquals(('a', [['']], OrderedDict(), None), _parse_source_arg('a:'))
        self.assertEquals(('a', [['b']], OrderedDict(), None), _parse_source_arg('a:b'))
        self.assertEquals(('a', [['b']], OrderedDict([('c', '8')]), None), _parse_source_arg('a:b:c=8'))
        self.assertEquals(('a', [['c'], ['e']], OrderedDict([('b', '1'), ('d', '2')]), None), _parse_source_arg('a:b=1:c:d=2:e'))
