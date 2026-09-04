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

    def test_wait_operations_scans_skipped_blocks(self):
        """With 1s blocks the head advances 2+ levels between polls; the op sits in a block never seen as head."""
        opg_hash = 'ooStubInjectedOperationHash'
        included = {'hash': opg_hash, 'contents': [{'kind': 'transaction'}]}
        b1, b2, b3 = 'BLstub1', 'BLstub2', 'BLstub3'
        polls = iter([b1, b1, b3, b3, b3])  # head is b1 at injection, then jumps straight to b3
        routes = {
            '/chains/main/blocks/head/hash': lambda *_: (200, next(polls)),
        }
        for level, (block, predecessor) in enumerate([(b1, 'BLstub0'), (b2, b1), (b3, b2)], start=1):
            routes[f'/chains/main/blocks/{block}/hash'] = block
            routes[f'/chains/main/blocks/{block}/header'] = {
                'hash': block,
                'level': level,
                'predecessor': predecessor,
                'timestamp': '2026-09-04T03:44:53Z',
            }
            routes[f'/chains/main/blocks/{block}/context/constants'] = {'minimal_block_delay': '1'}
            routes[f'/chains/main/blocks/{block}/operation_hashes'] = [[], [], [], [opg_hash] if block == b2 else []]
        routes[f'/chains/main/blocks/{b2}/operations/3/0'] = included
        with SequencerStub(extra_routes=routes) as node:
            client = pytezos.using(shell=STUB_URL, key=alice_key)
            operations = client.shell.wait_operations([opg_hash], ttl=3, min_confirmations=1, current_block_hash=b1)
        self.assertEqual([included], operations)
        self.assertEqual(1, node.count(f'/blocks/{b2}/operation_hashes'), 'the skipped block must be scanned once')
