from unittest import TestCase

from tests import get_data
from pytezos.michelson.contract import ContractStorage


class BigMapCodingTestop8T7J(TestCase):

    def setUp(self):
        self.maxDiff = None

    def test_big_map_op8T7J(self):    
        section = get_data(
            path='big_map_diff/op8T7JNCH817UoSfNhDmmnY6AWkYduKZdJ6PhCxE33NxtDU8N3P/storage_section.json')
        storage = ContractStorage(section)
            
        big_map_diff = get_data(
            path='big_map_diff/op8T7JNCH817UoSfNhDmmnY6AWkYduKZdJ6PhCxE33NxtDU8N3P/big_map_diff.json')
        expected = [
            dict(key=item['key'], value=item.get('value'))
            for item in big_map_diff
        ]
        
        big_map = storage.big_map_diff_decode(expected)
        actual = storage.big_map_diff_encode(big_map)
        self.assertEqual(expected, actual)
