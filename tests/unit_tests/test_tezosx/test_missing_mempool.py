"""A node without a mempool (Tezos X sequencer) must not break sending and waiting."""

from unittest import TestCase

from pytezos import pytezos
from pytezos.context.mixin import alice_key
from pytezos.rpc.node import RpcError
from pytezos.rpc.node import RpcNode
from pytezos.rpc.node import RpcNotFoundError

from .sequencer_stub import HEAD_HASH
from .sequencer_stub import STUB_URL
from .sequencer_stub import SequencerStub


class TestMissingMempool(TestCase):
    def test_404_is_a_typed_error(self):
        with SequencerStub(), self.assertRaises(RpcNotFoundError) as ctx:
            RpcNode(STUB_URL).get('/chains/main/mempool/pending_operations')
        self.assertIsInstance(ctx.exception, RpcError)
        self.assertIn('pending_operations', str(ctx.exception))

    def test_counter_offset_is_zero_without_mempool(self):
        with SequencerStub() as node:
            client = pytezos.using(shell=STUB_URL, key=alice_key)
            self.assertEqual(0, client.context.get_counter_offset())
        self.assertEqual(1, node.count('/mempool/pending_operations'))

    def test_wait_operations_without_mempool(self):
        opg_hash = 'ooStubInjectedOperationHash'
        included = {'hash': opg_hash, 'contents': [{'kind': 'transaction'}]}
        routes = {
            f'/chains/main/blocks/{HEAD_HASH}/operation_hashes': [[], [], [], [opg_hash]],
            f'/chains/main/blocks/{HEAD_HASH}/operations/3/0': included,
        }
        with SequencerStub(extra_routes=routes):
            client = pytezos.using(shell=STUB_URL, key=alice_key)
            operations = client.shell.wait_operations([opg_hash], ttl=2, min_confirmations=1)
        self.assertEqual([included], operations)
