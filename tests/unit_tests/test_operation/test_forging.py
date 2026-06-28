import json
from os.path import dirname
from os.path import join
from unittest import TestCase

from parameterized import parameterized  # type: ignore

from pytezos import pytezos
from pytezos.crypto.encoding import base58_encode
from pytezos.operation.forge import forge_reveal
from pytezos.operation.group import OperationGroup


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
        # GAP-1: a tz5 reveal embeds an ML-DSA-44 (mdpk) public key, so
        # forge_reveal -> forge_public_key must handle it. RED until the
        # forge_public_key fix (mdpk -> tag \x04) lands.
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
