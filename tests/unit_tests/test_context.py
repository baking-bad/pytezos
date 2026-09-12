from unittest import TestCase
from unittest.mock import Mock
from unittest.mock import patch

from pytezos.context.impl import ExecutionContext
from pytezos.crypto.key import Key
from pytezos.rpc.node import RpcError
from pytezos.rpc.node import RpcForbiddenError
from pytezos.rpc.node import RpcNode
from pytezos.rpc.node import RpcNotFoundError
from pytezos.rpc.shell import ShellQuery


class TestContext(TestCase):
    def test_sandboxed(self) -> None:
        # Arrange
        # TODO: Update with jakartanet response
        public_version_response = {
            "version": {
                "major": 8,
                "minor": 2,
                "additional_info": "release",
            },
            "network_version": {
                "chain_name": "TEZOS_EDO2NET_2021-02-11T14:00:00Z",
                "distributed_db_version": 1,
                "p2p_version": 1,
            },
            "commit_info": {
                "commit_hash": "6102c808a21b32e732ab9bb1825761cd056f3e86",
                "commit_date": "2021-02-10 22:57:06 +0100",
            },
        }
        sandboxed_version_response = {
            "version": {
                "major": 8,
                "minor": 2,
                "additional_info": "release",
            },
            "network_version": {
                "chain_name": "SANDBOXED_TEZOS",
                "distributed_db_version": 1,
                "p2p_version": 1,
            },
            "commit_info": {
                "commit_hash": "6102c808a21b32e732ab9bb1825761cd056f3e86",
                "commit_date": "2021-02-10 22:57:06 +0100",
            },
        }

        # Act
        with patch("pytezos.rpc.query.RpcQuery.__call__") as rpc_mock:
            rpc_mock.return_value = public_version_response
            public_result = ExecutionContext(shell=ShellQuery(None)).sandboxed  # type: ignore

        with patch("pytezos.rpc.query.RpcQuery.__call__") as rpc_mock:
            rpc_mock.return_value = sandboxed_version_response
            sandboxed_result = ExecutionContext(shell=ShellQuery(None)).sandboxed  # type: ignore

        # Assert
        self.assertFalse(public_result)
        self.assertTrue(sandboxed_result)


def op(*sources: str) -> dict:
    return {'hash': 'oo' + ''.join(sources)[:20], 'contents': [{'kind': 'transaction', 'source': s} for s in sources]}


class TestCounterOffset(TestCase):
    def setUp(self) -> None:
        self.key = Key.generate(export=False)
        self.key_hash = self.key.public_key_hash()
        self.other = 'tz1KqTpEZ7Yob7QbPE4Hy4Wo8fHG8LhKxZSx'
        self.context = ExecutionContext(key=self.key, shell=ShellQuery(None))  # type: ignore

    def get_counter_offset(self, response=None, side_effect=None) -> int:
        with patch('pytezos.rpc.query.RpcQuery.__call__') as rpc_mock:
            rpc_mock.return_value = response
            rpc_mock.side_effect = side_effect
            return self.context.get_counter_offset()

    def test_counts_validated_and_unprocessed_of_own_key(self) -> None:
        response = {
            'validated': [op(self.key_hash, self.key_hash), op(self.other)],
            'unprocessed': [op(self.key_hash)],
            'refused': [op(self.key_hash)],
            'branch_delayed': [op(self.key_hash)],
        }
        self.assertEqual(3, self.get_counter_offset(response))

    def test_counts_legacy_applied_key(self) -> None:
        response = {
            'applied': [op(self.key_hash, self.key_hash), op(self.other)],
            'unprocessed': [op(self.key_hash)],
        }
        self.assertEqual(3, self.get_counter_offset(response))

    def test_empty_validated_does_not_read_applied(self) -> None:
        response = {
            'validated': [],
            'applied': [op(self.key_hash)],
            'unprocessed': [op(self.key_hash)],
        }
        self.assertEqual(1, self.get_counter_offset(response))

    def test_normalizes_hash_operation_pairs(self) -> None:
        response = {
            'validated': [['ooHash1', {'contents': [{'kind': 'transaction', 'source': self.key_hash}]}]],
            'unprocessed': [['ooHash2', {'contents': [{'kind': 'transaction', 'source': self.other}]}]],
        }
        self.assertEqual(1, self.get_counter_offset(response))

    def test_query_parameters(self) -> None:
        with patch('pytezos.rpc.query.RpcQuery.__call__') as rpc_mock:
            rpc_mock.return_value = {'validated': []}
            self.context.get_counter_offset()
        rpc_mock.assert_called_once_with(
            source=self.key_hash,
            refused='false',
            outdated='false',
            branch_refused='false',
            branch_delayed='false',
        )

    def test_unfiltered_node_response_is_filtered_client_side(self) -> None:
        response = {
            'validated': [op(self.other), op(self.key_hash, self.other), op('tz1VSUr8wwNhLAzempoch5d6hLRiTh8Cjcjb')],
        }
        self.assertEqual(1, self.get_counter_offset(response))

    def test_mempool_forbidden_gives_zero(self) -> None:
        self.assertEqual(0, self.get_counter_offset(side_effect=RpcForbiddenError('Forbidden: mempool')))
        self.assertEqual(0, self.get_counter_offset(side_effect=RpcNotFoundError('Not found: mempool')))

    def test_http_status_through_rpc_node(self) -> None:
        context = ExecutionContext(key=self.key, shell=ShellQuery(RpcNode('http://localhost:8732')))
        for status_code in (401, 403, 404):
            with self.subTest(status_code=status_code):
                res = Mock(status_code=status_code, text='', headers={'content-type': 'text/html'})
                with patch('pytezos.rpc.node.requests.request', return_value=res):
                    self.assertEqual(0, context.get_counter_offset())
        res = Mock(status_code=500, text='boom', headers={'content-type': 'text/html'})
        with patch('pytezos.rpc.node.requests.request', return_value=res), self.assertRaises(RpcError):
            context.get_counter_offset()

    def test_other_rpc_errors_propagate(self) -> None:
        with self.assertRaises(RpcError):
            self.get_counter_offset(side_effect=RpcError('boom'))

    def test_empty_mempool_and_missing_keys(self) -> None:
        self.assertEqual(0, self.get_counter_offset({}))
        self.assertEqual(0, self.get_counter_offset({'validated': []}))
