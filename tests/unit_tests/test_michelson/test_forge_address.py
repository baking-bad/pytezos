import pytest

from pytezos.michelson.forge import forge_address
from pytezos.michelson.forge import unforge_address


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
