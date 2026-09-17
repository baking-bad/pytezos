import logging
from unittest import skip

from pytezos.rpc.errors import RpcError
from pytezos.sandbox.node import SandboxedNodeTestCase
from pytezos.sandbox.parameters import sandbox_addresses

logging.basicConfig(level=logging.DEBUG)


class TransactionCounterTestCase(SandboxedNodeTestCase):
    @skip('Not applicable in Parisnet?')
    def test_1_send_multiple_transactions_non_batched(self) -> None:
        client = self.client
        # Only one manager operation per manager per block allowed
        with self.assertRaises(RpcError):
            for _ in range(3):
                client.transaction(
                    destination=sandbox_addresses['bootstrap3'],
                    amount=42,
                ).autofill(
                    gas_reserve=100000,
                ).sign().inject(min_confirmations=0)

        pending_operations = client.shell.mempool.pending_operations()
        self.assertEqual(1, len(pending_operations['validated']))
