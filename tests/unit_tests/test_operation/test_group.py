import json
from contextlib import suppress
from os.path import dirname
from os.path import join
from unittest import TestCase
from unittest.mock import MagicMock
from unittest.mock import patch

from pytezos.client import PyTezosClient
from pytezos.context.impl import ExecutionContext
from pytezos.crypto.key import Key
from pytezos.operation.group import OperationGroup
from pytezos.operation.result import OperationResult


class PendingMempoolContext(ExecutionContext):
    def get_counter_offset(self) -> int:
        return 3


def run_applied(opg: OperationGroup) -> dict:
    result = {'status': 'applied', 'consumed_milligas': '1000000', 'paid_storage_size_diff': '0'}
    return {'contents': [{**content, 'metadata': {'operation_result': result}} for content in opg.contents]}


class TestOperationGroup(TestCase):
    maxDiff = None

    @patch("pytezos.rpc.protocol.BlocksQuery.__getitem__")
    def test_fill(self, rpc_mock):
        # Arrange
        testmap = {
            "branch_offset_sandboxed": [5, None, True, 'head~5'],
            "branch_offset_not_sandboxed": [5, None, False, 'head~5'],
            "ttl_sandboxed": [None, 10, True, 'head~110'],
            "ttl_not_sandboxed": [None, 10, False, 'head~110'],
            "ttl_sandboxed_default": [None, None, True, 'head~0'],
            "ttl_not_sandboxed_default": [None, None, False, 'head~115'],
        }

        client = PyTezosClient()
        client.context.chain_id = 'NetXxkAx4woPLyu'
        client.context.protocol = 'PsFLorenaUUuikDWvMDr6fGBRG8kt3e3D3fHoXK1j1BFRxeSH4i'
        op = client.transaction(destination="")

        for name, (branch_offset, ttl, sandboxed, mock_call) in testmap.items():
            with self.subTest(name):
                # Act
                op.context._sandboxed = sandboxed
                with suppress(Exception):
                    op.fill(branch_offset=branch_offset, ttl=ttl, gas_limit=0, storage_limit=0, counter=0)

                # Assert
                rpc_mock.assert_called_with(mock_call)

    def test_operation_result(self):
        with open(join(dirname(__file__), 'data', 'op3GZiumMFEGWNPae1GDGEG2skKEibhEgusKc7XBG7gzxbSg5SD.json')) as f:
            data = json.loads(f.read())

        res = OperationResult.from_operation_group(data)
        self.assertEqual(1, len(res))
        self.assertEqual(6, len(res[0].lazy_diff))

    def test_autofill_ignores_pending_mempool_operations(self):
        # Arrange
        shell = MagicMock()
        shell.head.context.constants.return_value = {
            'hard_gas_limit_per_operation': '1040000',
            'hard_storage_limit_per_operation': '60000',
        }
        shell.blocks.__getitem__.return_value.hash.return_value = 'BLockGenesisGenesisGenesisGenesisGenesisf79b5d1CoW2'
        context = PendingMempoolContext(
            key=Key.generate(export=False),
            shell=shell,
            chain_id='NetXxkAx4woPLyu',
            protocol='PsFLorenaUUuikDWvMDr6fGBRG8kt3e3D3fHoXK1j1BFRxeSH4i',
            counter=41,
        )
        context._sandboxed = False
        opg = OperationGroup(context=context)
        for _ in range(3):
            opg = opg.transaction(destination='tz1KqTpEZ7Yob7QbPE4Hy4Wo8fHG8LhKxZSx', amount=1)

        # Act
        with patch.object(OperationGroup, 'run', run_applied):
            opg = opg.autofill()

        # Assert
        self.assertEqual(['42', '43', '44'], [content['counter'] for content in opg.contents])
        shell.mempool.pending_operations.from_source.assert_not_called()
