import json
from os.path import dirname
from os.path import join
from unittest import TestCase

from parameterized import parameterized  # type: ignore

from pytezos import pytezos
from pytezos.crypto.encoding import base58_encode
from pytezos.operation.forge import forge_entrypoint
from pytezos.operation.forge import forge_reveal
from pytezos.operation.forge import forge_transaction
from pytezos.operation.group import OperationGroup

# Single-byte tags from Octez `entrypoint_repr.ml` (proto 025); any other entrypoint is `ff` + length-prefixed name.
RESERVED_ENTRYPOINT_TAGS = [
    ('default', '00'),
    ('root', '01'),
    ('do', '02'),
    ('set_delegate', '03'),
    ('remove_delegate', '04'),
    ('deposit', '05'),
    ('stake', '06'),
    ('unstake', '07'),
    ('finalize_unstake', '08'),
    ('set_delegate_parameters', '09'),
]


class TestOperationForging(TestCase):
    @parameterized.expand(
        [
            ("ooFdR2Anyv7pHaehM2rK5DaUWaVv3wUkyR5mkm9u7Wd8jtQaXA9",),
            ("onewnQxJgwk384Bk6fuLmq7rFM5AePy2xLV1v475H4nog9Y9Haz",),
            ("onpsXDeuWpVH9oNd9XHDvUZMwekVrNS9rsdbp9f3LDbimLqZDrw",),
        ]
    )
    def test_operation_hash_is_correct(self, opg_hash):
        with open(join(dirname(__file__), 'data', f'{opg_hash}.json')) as f:
            data = json.loads(f.read())

        group = OperationGroup(
            context=pytezos.using('mumbainet').context,
            contents=data['contents'],
            chain_id=data['chain_id'],
            protocol=data['protocol'],
            branch=data['branch'],
            signature=data['signature'],
        )
        res = group.hash()
        self.assertEqual(opg_hash, res)

    def test_forge_reveal_with_tz5_account(self):
        # a tz5 reveal embeds an ML-DSA-44 (mdpk) public key, so
        # forge_reveal -> forge_public_key must tag it \x04.
        payload = bytes(range(256)) * 5 + bytes(32)
        content = {
            'kind': 'reveal',
            'source': 'tz5T7uDWfmUDvYw2kr6wfbe2ATYhRvKfLoFE',
            'fee': '0',
            'counter': '1',
            'gas_limit': '0',
            'storage_limit': '0',
            'public_key': base58_encode(payload, b'mdpk').decode(),
        }
        forged = forge_reveal(content)
        self.assertIsInstance(forged, bytes)
        self.assertIn(b'\x04' + payload, forged)  # tz5 pubkey, tag \x04

    @parameterized.expand(RESERVED_ENTRYPOINT_TAGS)
    def test_forge_entrypoint_reserved(self, entrypoint, tag_hex):
        self.assertEqual(bytes.fromhex(tag_hex), forge_entrypoint(entrypoint))

    def test_forge_entrypoint_named(self):
        self.assertEqual(b'\xff\x08transfer', forge_entrypoint('transfer'))

    # Expected bytes recorded from `helpers/forge/operations` on shadownet and mainnet (proto 025), 2026-09-11.
    @parameterized.expand(RESERVED_ENTRYPOINT_TAGS + [('transfer', 'ff087472616e73666572')])
    def test_forge_transaction_entrypoint_matches_node(self, entrypoint, entrypoint_hex):
        content = {
            'kind': 'transaction',
            'source': 'tz1KqTpEZ7Yob7QbPE4Hy4Wo8fHG8LhKxZSx',
            'fee': '1000',
            'counter': '1',
            'gas_limit': '1000',
            'storage_limit': '0',
            'amount': '1',
            'destination': 'KT1BEqzn5Wx8uJrZNvuS9DVHmLvG9td3fDLi',
            'parameters': {'entrypoint': entrypoint, 'value': {'int': '1'}},
        }
        head = (
            '6c0002298c03ed7d454a101eb7022bc95f7e5f41ac78e80701e8070001011d23c1d3d2f8a4ea5e8784b8f7ecf2ad304c0fe600ff'
        )
        tail = '000000020001'
        self.assertEqual(head + entrypoint_hex + tail, forge_transaction(content).hex())
