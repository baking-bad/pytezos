from unittest import TestCase
from unittest.mock import MagicMock

from pytezos import pytezos
from pytezos.client import PyTezosClient
from pytezos.michelson.forge import forge_address
from pytezos.operation.forge import forge_operation

DELEGATE = 'tz1VSUr8wwNhLAzempoch5d6hLRiTh8Cjcjb'


class TestDelegation(TestCase):
    def test_default_registers_self(self):
        content = pytezos.delegation().contents[0]
        self.assertEqual(
            {
                'kind': 'delegation',
                'source': '',
                'fee': '0',
                'counter': '0',
                'gas_limit': '0',
                'storage_limit': '0',
                'delegate': '',
            },
            content,
        )

    def test_explicit_delegate(self):
        content = pytezos.delegation(delegate=DELEGATE).contents[0]
        self.assertEqual(DELEGATE, content['delegate'])

    def test_none_omits_delegate_key(self):
        content = pytezos.delegation(delegate=None).contents[0]
        self.assertNotIn('delegate', content)
        self.assertEqual('delegation', content['kind'])

    def test_bulk_keeps_delegate_absent(self):
        content = pytezos.bulk(pytezos.delegation(delegate=None)).contents[0]
        self.assertNotIn('delegate', content)

    def test_fill(self):
        client = PyTezosClient()
        client.context.chain_id = 'NetXxkAx4woPLyu'
        client.context.protocol = 'PsFLorenaUUuikDWvMDr6fGBRG8kt3e3D3fHoXK1j1BFRxeSH4i'
        client.context.shell = MagicMock()
        client.context.shell.blocks.__getitem__.return_value.hash.return_value = (
            'BLockGenesisGenesisGenesisGenesisGenesisCCCCCeZbHb'
        )
        client.context.shell.head.context.constants.return_value = {
            'hard_gas_limit_per_operation': '1040000',
            'hard_storage_limit_per_operation': '60000',
        }
        source = client.key.public_key_hash()

        with self.subTest('default registers self'):
            content = client.delegation().fill(counter=1).contents[0]
            self.assertEqual(source, content['delegate'])

        with self.subTest('explicit delegate is kept'):
            content = client.delegation(delegate=DELEGATE).fill(counter=1).contents[0]
            self.assertEqual(DELEGATE, content['delegate'])

        with self.subTest('None removes delegate'):
            content = client.delegation(delegate=None).fill(counter=1).contents[0]
            self.assertNotIn('delegate', content)
            self.assertEqual(source, content['source'])

    def test_forge_without_delegate(self):
        opg = pytezos.delegation(delegate=None, source=DELEGATE, counter=1, fee=1000, gas_limit=1000)
        res = forge_operation(opg.contents[0])
        self.assertEqual('6e006b82198cb179e8306c1bedd08f12dc863f328886e80701e8070000', res.hex())
        self.assertTrue(res.endswith(b'\x00'))

    def test_forge_with_delegate(self):
        opg = pytezos.delegation(delegate=DELEGATE, source=DELEGATE, counter=1, fee=1000, gas_limit=1000)
        res = forge_operation(opg.contents[0])
        self.assertEqual(
            '6e006b82198cb179e8306c1bedd08f12dc863f328886e80701e80700ff006b82198cb179e8306c1bedd08f12dc863f328886',
            res.hex(),
        )
        self.assertTrue(res.endswith(b'\xff' + forge_address(DELEGATE, tz_only=True)))
