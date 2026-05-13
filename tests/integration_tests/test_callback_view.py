import pytest

from pytezos import pytezos


class TestCallbackView:
    def test_balance_of(self):
        usds = pytezos.using('mainnet').contract('KT1REEb5VxWRjcHm5GzDMwErMmNFftsE5Gpf')
        res = usds.balance_of(
            requests=[
                {'owner': 'tz1PNsHbJRejCnnYzbsQ1CR8wUdEQqVjWen1', 'token_id': 0},
                {'owner': 'tz1i2tE6hic2ASe9Kvy85ar5hGSSc58bYejT', 'token_id': 0},
                {'owner': 'tz2QegZQXyz8b74iTdaqKsGRF7YQb88Wu9CS', 'token_id': 0},
            ],
            callback=None,
        ).callback_view()
        assert res

    def test_initial_storage(self):
        usds = pytezos.using('mainnet').contract('KT1REEb5VxWRjcHm5GzDMwErMmNFftsE5Gpf')
        storage = usds.storage()
        storage['ledger'] = {'tz1PNsHbJRejCnnYzbsQ1CR8wUdEQqVjWen1': 42}
        res = usds.balance_of(
            requests=[
                {'owner': 'tz1PNsHbJRejCnnYzbsQ1CR8wUdEQqVjWen1', 'token_id': 0},
            ],
            callback=None,
        ).callback_view(storage=storage)
        assert res[0]['balance'] == 42

    @pytest.mark.skip('shadownet: Contract KT1G9uxhbEApw2Z7yvUA4WvqCedG2a48ggzc not found')
    def test_onchain_view(self):
        ci = pytezos.using('shadownet').contract('KT1G9uxhbEApw2Z7yvUA4WvqCedG2a48ggzc')
        res = ci.get_current_state().run_view()
        assert res
