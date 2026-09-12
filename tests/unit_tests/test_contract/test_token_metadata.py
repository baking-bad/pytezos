import json
from datetime import time
from os import listdir
from os.path import dirname
from os.path import join
from unittest import TestCase

from jsonschema import ValidationError  # type: ignore

from pytezos.contract.token_metadata import ContractTokenMetadata


class TokenMetadataTest(TestCase):
    token_metadata_path = join(dirname(__file__), 'token_metadata')

    def load_fixture(self, filename):
        with open(join(self.token_metadata_path, filename)) as file:
            return json.load(file)

    def test_from_json(self):
        for filename in listdir(self.token_metadata_path):
            with self.subTest(filename):
                ContractTokenMetadata.from_json(self.load_fixture(filename))

    def test_rights_uri_spellings(self):
        cases = [
            ({'decimals': 0, 'rightsUri': 'a'}, 'a'),
            ({'decimals': 0, 'rightUri': 'b'}, 'b'),
            ({'decimals': 0, 'rightsUri': 'a', 'rightUri': 'b'}, 'a'),
            ({'decimals': 0, 'rightUri': 1}, None),
            ({'decimals': 0, 'rightUri': None}, None),
            ({'decimals': 0}, None),
        ]
        for metadata_json, expected in cases:
            with self.subTest(metadata_json):
                res = ContractTokenMetadata.from_json(dict(metadata_json))
                self.assertEqual(expected, res.rightsUri)
                self.assertEqual(metadata_json, res.raw)

    def test_unknown_top_level_key_tolerated(self):
        res = ContractTokenMetadata.from_json({'decimals': 0, 'foo': 'bar'})
        self.assertEqual('bar', res.raw['foo'])

    def test_rights_uri_type_still_checked(self):
        with self.assertRaises(ValidationError):
            ContractTokenMetadata.validate_token_metadata_json({'decimals': 0, 'rightsUri': 1})

    def test_unknown_format_key_still_rejected(self):
        with self.assertRaises(ValidationError):
            ContractTokenMetadata.from_json({'decimals': 0, 'formats': [{'uri': 'x', 'extra': 1}]})

    def test_fixture_rights_uri(self):
        versum = ContractTokenMetadata.from_json(self.load_fixture('example-030-versum-rightUri.json'))
        self.assertEqual('ipfs://QmNW3M7k1us4EX5QUo7MNDtapFLhHUjaLRbThshVqZzxos', versum.rightsUri)
        self.assertEqual('ipfs://Qmb55M6wFiAB6yU5PcBqc5GAj7nbioRY1GTh9aYn5wT4sQ', versum.raw['pinUri'])

        shinoda = ContractTokenMetadata.from_json(self.load_fixture('example-040-shinoda-rightsUri.json'))
        self.assertEqual('https://www.mikeshinoda.com/NFTTerms', shinoda.rightsUri)

        hen = ContractTokenMetadata.from_json(self.load_fixture('example-050-hen-rightsUri.json'))
        self.assertEqual('ipfs://QmYvuWf4cHsUoUmFAyPKYaUYgTMWoopZBJ6o6DH1W1qP7o', hen.rightsUri)
        self.assertEqual('https://teia.art/mint', hen.raw['mintingTool'])

    def test_language_and_should_prefer_symbol_types(self):
        res = ContractTokenMetadata.from_json(self.load_fixture('example-030-versum-rightUri.json'))
        self.assertEqual('en', res.language)
        self.assertIs(False, res.shouldPreferSymbol)

    def test_format_duration(self):
        res = ContractTokenMetadata.from_json(self.load_fixture('example-040-shinoda-rightsUri.json'))
        self.assertEqual(time(0, 6, 45), res.formats[0].duration)
