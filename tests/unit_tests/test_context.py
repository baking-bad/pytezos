from unittest import TestCase
from unittest.mock import patch

from pytezos import pytezos
from pytezos.context.impl import DEFAULT_IPFS_GATEWAY
from pytezos.context.impl import ExecutionContext
from pytezos.contract.interface import ContractInterface
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

    def test_default_ipfs_gateway(self) -> None:
        self.assertEqual('https://ipfs.filebase.io/ipfs', DEFAULT_IPFS_GATEWAY)
        self.assertEqual(DEFAULT_IPFS_GATEWAY, ExecutionContext().ipfs_gateway)

    def test_ipfs_gateway_inherited(self) -> None:
        client = pytezos.using(ipfs_gateway='https://gw.example/ipfs/')

        self.assertEqual('https://gw.example/ipfs', client.context.ipfs_gateway)
        self.assertEqual('https://gw.example/ipfs', client._spawn_context().ipfs_gateway)

        contract = ContractInterface.from_michelson(
            'parameter unit; storage unit; code { CDR; NIL operation; PAIR }',
            context=client.context,
        )
        self.assertEqual('https://gw.example/ipfs', contract.context.ipfs_gateway)
        self.assertEqual('https://gw.example/ipfs', contract.using(block_id=5).context.ipfs_gateway)
        self.assertEqual(
            'https://other.example/ipfs', contract.using(ipfs_gateway='https://other.example/ipfs').context.ipfs_gateway
        )
