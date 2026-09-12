import json
from os import listdir
from os.path import dirname
from os.path import join
from unittest import TestCase
from unittest.mock import patch

import requests

from pytezos.context.impl import ExecutionContext
from pytezos.contract.metadata import ContractMetadata


def make_response(status_code: int, content: bytes, url: str) -> requests.Response:
    res = requests.Response()
    res.status_code = status_code
    res._content = content
    res.url = url
    return res


class MetadataTest(TestCase):
    metadata_path = join(dirname(__file__), 'metadata')

    def test_from_json(self):
        for filename in listdir(self.metadata_path):
            with self.subTest(filename), open(join(self.metadata_path, filename)) as file:
                metadata_json = json.load(file)
                ContractMetadata.from_json(metadata_json)

    def test_from_ipfs(self):
        with open(join(self.metadata_path, 'example-001.json'), 'rb') as file:
            content = file.read()
        context = ExecutionContext(ipfs_gateway='https://gw.example/ipfs')

        with patch('pytezos.contract.requests.get') as get_mock:
            get_mock.return_value = make_response(200, content, 'https://gw.example/ipfs/QmX')
            metadata = ContractMetadata.from_ipfs('QmX', context)

        get_mock.assert_called_once_with('https://gw.example/ipfs/QmX', timeout=60)
        self.assertEqual(json.loads(content), metadata.raw)

    def test_from_ipfs_http_error(self):
        context = ExecutionContext(ipfs_gateway='https://gw.example/ipfs')

        with patch('pytezos.contract.requests.get') as get_mock:
            get_mock.return_value = make_response(429, b'gateway is switching', 'https://gw.example/ipfs/QmX')
            with self.assertRaises(requests.RequestException) as cm:
                ContractMetadata.from_ipfs('QmX', context)

        message = str(cm.exception)
        self.assertIn('https://gw.example/ipfs', message)
        self.assertIn('QmX', message)
        self.assertIn('ipfs_gateway', message)
        self.assertEqual(429, cm.exception.response.status_code)
        self.assertIsInstance(cm.exception.__cause__, requests.HTTPError)

    def test_from_ipfs_non_json_body(self):
        context = ExecutionContext(ipfs_gateway='https://gw.example/ipfs')

        with patch('pytezos.contract.requests.get') as get_mock:
            get_mock.return_value = make_response(200, b'<html>brownout</html>', 'https://gw.example/ipfs/QmX')
            with self.assertRaises(requests.RequestException) as cm:
                ContractMetadata.from_ipfs('QmX', context)

        message = str(cm.exception)
        self.assertIn('https://gw.example/ipfs', message)
        self.assertIn('QmX', message)
        self.assertIn('ipfs_gateway', message)

    def test_from_ipfs_connection_error(self):
        context = ExecutionContext(ipfs_gateway='https://gw.example/ipfs')

        with patch('pytezos.contract.requests.get') as get_mock:
            get_mock.side_effect = requests.ConnectionError('name resolution failed')
            with self.assertRaises(requests.RequestException) as cm:
                ContractMetadata.from_ipfs('QmX', context)

        message = str(cm.exception)
        self.assertIn('https://gw.example/ipfs', message)
        self.assertIn('name resolution failed', message)
        self.assertIn('ipfs_gateway', message)

    def test_from_url_http_error(self):
        with patch('pytezos.contract.requests.get') as get_mock:
            get_mock.return_value = make_response(404, b'not found', 'https://example.org/metadata.json')
            with self.assertRaises(requests.HTTPError):
                ContractMetadata.from_url('https://example.org/metadata.json')
