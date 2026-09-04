"""Fee thresholds come from the node's mempool filter instead of hardcoded mainnet defaults."""

from unittest import TestCase

from pytezos import pytezos
from pytezos.context.mixin import alice_key
from pytezos.context.mixin import alice_key_hash
from pytezos.operation.fees import FeeThresholds
from pytezos.operation.fees import calculate_fee

from .sequencer_stub import PREVIEWNET_MEMPOOL_FILTER
from .sequencer_stub import STUB_URL
from .sequencer_stub import SequencerStub

TRANSACTION = {
    'kind': 'transaction',
    'source': alice_key_hash,
    'fee': '0',
    'counter': '1',
    'gas_limit': '1000',
    'storage_limit': '0',
    'amount': '1',
    'destination': 'tz1grSQDByRpnVs7sPtaprNZRp531ZKz6Jmm',
}


class TestFeeThresholds(TestCase):
    def test_defaults_match_mainnet(self):
        self.assertEqual(FeeThresholds(100, 1, 100), FeeThresholds())

    def test_from_mempool_filter(self):
        thresholds = FeeThresholds.from_mempool_filter(PREVIEWNET_MEMPOOL_FILTER)
        self.assertEqual(
            FeeThresholds(minimal_fees=100, minimal_mutez_per_byte=4, minimal_nanotez_per_gas_unit=45), thresholds
        )

    def test_per_byte_is_rounded_up(self):
        thresholds = FeeThresholds.from_mempool_filter(
            {**PREVIEWNET_MEMPOOL_FILTER, 'minimal_nanotez_per_byte': ['1500', '1']}
        )
        self.assertEqual(2, thresholds.minimal_mutez_per_byte)

    def test_calculate_fee_honours_thresholds(self):
        previewnet = FeeThresholds.from_mempool_filter(PREVIEWNET_MEMPOOL_FILTER)
        default = calculate_fee(TRANSACTION, consumed_gas=1000, extra_size=0, reserve=0)
        adjusted = calculate_fee(TRANSACTION, consumed_gas=1000, extra_size=0, reserve=0, thresholds=previewnet)
        size = default - 100 - 100  # minimal_fees + 1000 gas * 100 nanotez at mainnet rates
        self.assertEqual(100 + 4 * size + 45, adjusted)

    def test_client_reads_thresholds_from_node(self):
        with SequencerStub() as node:
            client = pytezos.using(shell=STUB_URL, key=alice_key, fee_thresholds='node')
            self.assertEqual(FeeThresholds(100, 4, 45), client.context.get_fee_thresholds())
            self.assertEqual(FeeThresholds(100, 4, 45), client.context.get_fee_thresholds())
        self.assertEqual(1, node.count('/mempool/filter'), 'filter must be read once per client')

    def test_autofill_quotes_node_thresholds(self):
        with SequencerStub() as node:
            node.add_account(alice_key_hash, counter=7)
            client = pytezos.using(shell=STUB_URL, key=alice_key)
            default_fee = int(client.transaction(destination=alice_key_hash, amount=1).autofill().contents[0]['fee'])
            client = client.using(fee_thresholds='node')
            node_fee = int(client.transaction(destination=alice_key_hash, amount=1).autofill().contents[0]['fee'])
        self.assertGreater(node_fee, default_fee, 'previewnet charges 4 mutez/byte, mainnet defaults quote 1')
        # Same op, same size: the difference is exactly the per-byte and per-gas deltas.
        gas = 169 + 100  # ceil(168420 milligas) + DEFAULT_GAS_RESERVE
        size = default_fee - 10 - 100 - gas * 100 // 1000  # reserve, minimal_fees, gas component at 100 nanotez
        self.assertEqual(default_fee - size - gas * 100 // 1000 + 4 * size + gas * 45 // 1000, node_fee)
