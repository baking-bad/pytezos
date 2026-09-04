"""Live checks against the public Tezos X previewnet Michelson sequencer.

Read-only tests need no key. The write test runs only with `TEZOSX_SECRET_KEY` set to a
funded previewnet account (faucet: see https://github.com/trilitech/tezos-x-previewnet).
"""

import os
from unittest import TestCase
from unittest import skipUnless

from pytezos import pytezos
from pytezos.operation.fees import FeeThresholds
from pytezos.rpc.node import RpcNotFoundError

PREVIEWNET_RPC = os.environ.get('TEZOSX_RPC_URL', 'https://michelson.previewnet.tezosx.nomadic-labs.com')
PREVIEWNET_CHAIN_ID = 'NetXY2oPPzkxUW1'
SECRET_KEY = os.environ.get('TEZOSX_SECRET_KEY')


class TestTezosXPreviewnet(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = pytezos.using(
            shell=PREVIEWNET_RPC, key='tz1PSJR6wBtoiv56Uz1w1bBxeoBnWpDYMwV7', fee_thresholds='node'
        )

    def test_chain_is_previewnet(self):
        self.assertEqual(PREVIEWNET_CHAIN_ID, self.client.shell.chains.main.chain_id())

    def test_sequencer_has_no_mempool(self):
        """The assumption every fallback rests on: pending_operations 404s on the sequencer."""
        with self.assertRaises(RpcNotFoundError):
            self.client.shell.mempool.pending_operations()

    def test_counter_offset_survives_missing_mempool(self):
        self.assertEqual(0, self.client.context.get_counter_offset())

    def test_fee_thresholds_come_from_node(self):
        thresholds = self.client.context.get_fee_thresholds()
        self.assertIsInstance(thresholds, FeeThresholds)
        self.assertNotEqual(FeeThresholds(), thresholds, 'previewnet runs a non-mainnet fee policy')
        self.assertGreaterEqual(thresholds.minimal_mutez_per_byte, 1)

    @skipUnless(SECRET_KEY, 'TEZOSX_SECRET_KEY not set')
    def test_transfer_round_trip(self):
        """Send 1 mutez to self and wait for inclusion without any mempool access."""
        client = pytezos.using(shell=PREVIEWNET_RPC, key=SECRET_KEY, fee_thresholds='node')
        opg = client.transaction(destination=client.key.public_key_hash(), amount=1).send(min_confirmations=1)
        self.assertIsNotNone(opg.opg_hash)
        included = client.shell.blocks[-30:].find_operation(opg.opg_hash)
        self.assertEqual('applied', included['contents'][0]['metadata']['operation_result']['status'])
