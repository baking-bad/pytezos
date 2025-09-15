import pytest

from pytezos.context.mixin import alice_key
from pytezos.sandbox.node import SandboxedNodeTestCase
from pytezos.sandbox.parameters import sandbox_addresses
from pytezos.sandbox.parameters import sandbox_commitment


# NOTE: Node won't be wiped between tests so alphabetical order of method names matters
class SandboxTestCase(SandboxedNodeTestCase):
    def test_1_activate_protocol(self) -> None:
        header = self.client.shell.head.header()
        self.assertIsNotNone(header.get('content'))

    def test_2_bake_empty_block(self) -> None:
        self.bake_block()

    # FIXME: Change `alice` back too `bootstrap3`
    def test_3_create_transaction(self) -> None:
        opg = (
            self.client.transaction(
                # destination=sandbox_addresses['bootstrap3'],
                # amount=42,
                destination=sandbox_addresses['alice'],
                amount=4200,
            )
            .fill()
            .sign()
            .inject(min_confirmations=0)
        )
        self.assertIsNotNone(self.client.shell.mempool.pending_operations[opg['hash']])

    # FIXME: Change `alice` back too `bootstrap3`
    def test_4_bake_block(self) -> None:
        self.bake_block()
        # bootstrap3 = self.client.shell.contracts[sandbox_addresses['bootstrap3']]()
        # self.assertEqual(3800000316708, int(bootstrap3['balance']))
        alice = self.client.shell.contracts[sandbox_addresses['alice']]()
        self.assertEqual(4200, int(alice['balance']))

    @pytest.mark.skip('FIXME: proto.021-PsQuebec.validate.operation.invalid_activation')
    def test_5_activate_account(self) -> None:
        client = self.get_client(key=sandbox_commitment)
        client.activate_account().autofill().sign().inject()
        self.bake_block()
        self.assertEqual('100500000000', client.account()['balance'])

    # FIXME: Change `alice` back to `sandbox_commitment`
    def test_6_reveal_pk_and_send_tez(self) -> None:
        # client = self.get_client(key=sandbox_commitment)
        client = self.get_client(alice_key)
        res = (
            client.reveal()
            # .transaction(destination=sandbox_addresses['bootstrap4'], amount=1000000)
            .transaction(destination=sandbox_addresses['bootstrap4'], amount=69)
            .autofill()
            .sign()
            .inject()
        )
        balance_change = sum(int(op.get('amount', 0)) + int(op['fee']) for op in res['contents'])
        self.bake_block()
        # self.assertEqual(100500000000 - balance_change, int(client.account()['balance']))
        self.assertEqual(3464, int(client.account()['balance']))

    def test_7_register_constant(self):
        self.client.register_global_constant({'int': '12345'}).autofill().sign().inject()
        self.bake_block()
