import pytest

from pytezos.crypto.encoding import base58_encode
from pytezos.michelson.forge import forge_address
from pytezos.michelson.forge import forge_public_key
from pytezos.michelson.forge import unforge_address
from pytezos.michelson.forge import unforge_public_key


class TestForgeAddress:
    @pytest.mark.parametrize(
        ('address', 'forged_hex'),
        [
            ('tz1eKkWU5hGtfLUiqNpucHrXymm83z3DG9Sq', '0000ccf564a5a0bdb15c3dbdf84d68dacac3e1f968a3'),
            ('tz4F76GBmuLgXvUjLb2gfeBeM6fBf6EsuD1T', '000342eb77f76946e67e2eeefc47ed6a56b61e5cdbad'),
            ('tz5T7uDWfmUDvYw2kr6wfbe2ATYhRvKfLoFE', '000442eb77f76946e67e2eeefc47ed6a56b61e5cdbad'),
        ],
    )
    def test_forge_unforge_round_trip(self, address: str, forged_hex: str):
        forged = forge_address(address)
        assert forged.hex() == forged_hex
        assert unforge_address(forged) == address

    def test_forge_unforge_tz5_key_hash_only(self):
        address = 'tz5T7uDWfmUDvYw2kr6wfbe2ATYhRvKfLoFE'
        forged = forge_address(address, tz_only=True)
        assert forged.hex() == '0442eb77f76946e67e2eeefc47ed6a56b61e5cdbad'
        assert unforge_address(forged) == address


class TestForgePublicKey:
    # GAP-1: tz5 / ML-DSA-44 reveals embed an `mdpk` public key, which is forged
    # by forge_public_key (NOT forge_address). These currently stop at BLpk (tag
    # \x03) and raise — RED until the forge_public_key/unforge_public_key fix
    # (add `mdpk` -> tag \x04) lands.
    def test_forge_unforge_tz5_mdpk_round_trip(self):
        # synthetic ML-DSA-44 public key: exactly 1312 bytes of mdpk payload
        payload = bytes(range(256)) * 5 + bytes(32)
        assert len(payload) == 1312
        mdpk = base58_encode(payload, b'mdpk').decode()

        forged = forge_public_key(mdpk)
        assert forged[:1] == b'\x04'  # tz5 / ML-DSA-44 tag
        assert forged == b'\x04' + payload
        assert unforge_public_key(forged) == mdpk
