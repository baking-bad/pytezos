import json
from os import listdir
from os.path import dirname
from os.path import join
from unittest import TestCase
from unittest.mock import patch

import requests

from pytezos.context.impl import ExecutionContext
from pytezos.contract.token_metadata import ContractTokenMetadata


def make_response(status_code: int, content: bytes, url: str) -> requests.Response:
    res = requests.Response()
    res.status_code = status_code
    res._content = content
    res.url = url
    return res


class TokenMetadataTest(TestCase):
    token_metadata_path = join(dirname(__file__), 'token_metadata')

    def test_from_json(self):
        for filename in listdir(self.token_metadata_path):
            with self.subTest(filename), open(join(self.token_metadata_path, filename)) as file:
                metadata_json = json.load(file)
                ContractTokenMetadata.from_json(metadata_json)

    def test_from_ipfs(self):
        with open(join(self.token_metadata_path, 'example-000-base.json'), 'rb') as file:
            content = file.read()
        context = ExecutionContext(ipfs_gateway='https://gw.example/ipfs')

        with patch('pytezos.contract.requests.get') as get_mock:
            get_mock.return_value = make_response(200, content, 'https://gw.example/ipfs/QmX')
            token_metadata = ContractTokenMetadata.from_ipfs('QmX', context)

        get_mock.assert_called_once_with('https://gw.example/ipfs/QmX', timeout=60)
        self.assertEqual(json.loads(content)['name'], token_metadata.name)

    def test_from_ipfs_http_error(self):
        context = ExecutionContext(ipfs_gateway='https://gw.example/ipfs')

        with patch('pytezos.contract.requests.get') as get_mock:
            get_mock.return_value = make_response(429, b'gateway is switching', 'https://gw.example/ipfs/QmX')
            with self.assertRaises(requests.RequestException) as cm:
                ContractTokenMetadata.from_ipfs('QmX', context)

        message = str(cm.exception)
        self.assertIn('https://gw.example/ipfs', message)
        self.assertIn('QmX', message)
        self.assertIn('ipfs_gateway', message)
        self.assertEqual(429, cm.exception.response.status_code)
