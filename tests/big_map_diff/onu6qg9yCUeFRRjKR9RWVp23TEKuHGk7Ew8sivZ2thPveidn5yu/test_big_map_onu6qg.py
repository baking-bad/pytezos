from unittest import TestCase

from tests import get_data
from pytezos.michelson.contract import ContractStorage


class BigMapCodingTestonu6qg(TestCase):

    def setUp(self):
        self.maxDiff = None

    def test_big_map_onu6qg(self):    
        section = get_data(
            path='big_map_diff/onu6qg9yCUeFRRjKR9RWVp23TEKuHGk7Ew8sivZ2thPveidn5yu/storage_section.json')
        storage = ContractStorage(section)
            
        big_map_diff = get_data(
            path='big_map_diff/onu6qg9yCUeFRRjKR9RWVp23TEKuHGk7Ew8sivZ2thPveidn5yu/big_map_diff.json')
        expected = [
            dict(key=item['key'], value=item.get('value'))
            for item in big_map_diff
        ]
        
        big_map = storage.big_map_diff_decode(expected)
        actual = storage.big_map_diff_encode(big_map)
        self.assertEqual(expected, actual)
