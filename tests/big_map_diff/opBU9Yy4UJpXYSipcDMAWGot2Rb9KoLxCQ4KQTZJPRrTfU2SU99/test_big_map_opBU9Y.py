from unittest import TestCase

from tests import get_data
from pytezos.michelson.contract import ContractStorage


class BigMapCodingTestopBU9Y(TestCase):

    def setUp(self):
        self.maxDiff = None

    def test_big_map_opBU9Y(self):    
        section = get_data(
            path='big_map_diff/opBU9Yy4UJpXYSipcDMAWGot2Rb9KoLxCQ4KQTZJPRrTfU2SU99/storage_section.json')
        storage = ContractStorage(section)
            
        big_map_diff = get_data(
            path='big_map_diff/opBU9Yy4UJpXYSipcDMAWGot2Rb9KoLxCQ4KQTZJPRrTfU2SU99/big_map_diff.json')
        expected = [
            dict(key=item['key'], value=item.get('value'))
            for item in big_map_diff
        ]
        
        big_map = storage.big_map_diff_decode(expected)
        actual = storage.big_map_diff_encode(big_map)
        self.assertEqual(expected, actual)
