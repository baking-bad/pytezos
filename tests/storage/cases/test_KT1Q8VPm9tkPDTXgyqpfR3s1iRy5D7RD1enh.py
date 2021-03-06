from unittest import TestCase

from tests import get_data
from pytezos.michelson.converter import build_schema, decode_micheline, encode_micheline, micheline_to_michelson


class StorageTestKT1Q8VPm9tkPDTXgyqpfR3s1iRy5D7RD1enh(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.maxDiff = None
        cls.contract = get_data('storage/carthagenet/KT1Q8VPm9tkPDTXgyqpfR3s1iRy5D7RD1enh.json')

    def test_storage_encoding_KT1Q8VPm9tkPDTXgyqpfR3s1iRy5D7RD1enh(self):
        type_expr = self.contract['script']['code'][1]
        val_expr = self.contract['script']['storage']
        schema = build_schema(type_expr)
        decoded = decode_micheline(val_expr, type_expr, schema)
        actual = encode_micheline(decoded, schema)
        self.assertEqual(val_expr, actual)

    def test_storage_schema_KT1Q8VPm9tkPDTXgyqpfR3s1iRy5D7RD1enh(self):
        _ = build_schema(self.contract['script']['code'][0])

    def test_storage_format_KT1Q8VPm9tkPDTXgyqpfR3s1iRy5D7RD1enh(self):
        _ = micheline_to_michelson(self.contract['script']['code'])
        _ = micheline_to_michelson(self.contract['script']['storage'])
