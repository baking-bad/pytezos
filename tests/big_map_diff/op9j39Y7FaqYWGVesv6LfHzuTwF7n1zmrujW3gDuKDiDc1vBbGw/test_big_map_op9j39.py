from unittest import TestCase

from tests import get_data
from pytezos.michelson.contract import ContractStorage


class BigMapCodingTestop9j39(TestCase):

    def setUp(self):
        self.maxDiff = None

    def test_big_map_op9j39(self):    
        section = get_data(
            path='big_map_diff/op9j39Y7FaqYWGVesv6LfHzuTwF7n1zmrujW3gDuKDiDc1vBbGw/storage_section.json')
        storage = ContractStorage(section)
            
        big_map_diff = get_data(
            path='big_map_diff/op9j39Y7FaqYWGVesv6LfHzuTwF7n1zmrujW3gDuKDiDc1vBbGw/big_map_diff.json')
        expected = [
            dict(key=item['key'], value=item.get('value'))
            for item in big_map_diff
        ]
        
        big_map = storage.big_map_diff_decode(expected)
        actual = storage.big_map_diff_encode(big_map)
        self.assertEqual(expected, actual)
