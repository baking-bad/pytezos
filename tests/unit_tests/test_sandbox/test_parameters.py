from pytezos.sandbox.parameters import LATEST
from pytezos.sandbox.parameters import USHUAIA
from pytezos.sandbox.parameters import protocol_hashes
from pytezos.sandbox.parameters import protocol_version


class TestUshuaiaParameters:
    def test_ushuaia_is_latest(self):
        assert LATEST == USHUAIA

    def test_ushuaia_hash(self):
        assert USHUAIA == 'PsUshuai9QapM5TGj1JpuVGkdxz5GykdnEvS6Rh8SUVrARvZLCY'

    def test_ushuaia_registered(self):
        assert protocol_hashes['ushuaia'] == USHUAIA
        assert protocol_version[USHUAIA] == 25
