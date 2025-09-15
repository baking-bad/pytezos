import json
from pathlib import Path
from typing import Any
from typing import Dict

from pytezos.crypto.key import Key

EDO = 'PtEdo2ZkT9oKpimTah6x2embF25oss54njMuPzkJTEi5RqfdZFA'
FLORENCE = 'PsFLorenaUUuikDWvMDr6fGBRG8kt3e3D3fHoXK1j1BFRxeSH4i'
GRANADA = 'PtGRANADsDU8R9daYKAgWnQYAJ64omN1o3KMGVCykShA97vQbvV'
HANGZHOU = 'PtHangz2aRngywmSRGGvrcTyMbbdpWdpFKuS4uMWxg2RaH9i1qx'
ITHACA = 'Psithaca2MLRFYargivpo7YvUr7wUDqyxrdhC5CQq78mRvimz6A'
JAKARTA = 'PtJakart2xVj7pYXJBXrqHgd82rdkLey5ZeeGwDgPp9rhQUbSqY'
KATHMANDU = 'PtKathmankSpLLDALzWw7CGD2j2MtyveTwboEYokqUCP4a1LxMg'
LIMA = 'PtLimaPtLMwfNinJi9rCfDPWea8dFgTZ1MeJ9f1m2SRic6ayiwW'
MUMBAI = 'PtMumbai2TmsJHNGRkD8v8YDbtao7BLUC3wjASn1inAKLFCjaH1'
NAIROBI = 'PtNairobiyssHuh87hEhfVBGCVrK3WnS8Z2FT4ymB5tAa4r1nQf'
OXFORD = 'ProxfordYmVfjWnRcgjWH36fW6PArwqykTFzotUxRs6gmTcZDuH'
PARIS = 'PtParisBxoLz5gzMmn3d9WBQNoPSZakgnkMC2VNuQ3KXfUtUQeZ'
PARISC = 'PsParisCZo7KAh1Z1smVd9ZMZ1HHn5gkzbM94V3PLCpknFWhUAi'
QUEBEC = 'PsQuebecnLByd3JwTiGadoG4nGWi3HYiLXUjkibeFV8dCFeVMUg'
RIO = 'PsRiotumaAMotcRoDWW1bysEhQy2n1M5fy8JgRp8jjRfHGmfeA7'
SEOUL = 'PtSeouLouXkxhg39oWzjxDWaCydNfR3RxCUrNe4Q9Ro8BTehcbh'
LATEST = SEOUL

protocol_hashes = {
    'edo': EDO,
    'florence': FLORENCE,
    'granada': GRANADA,
    'hangzhou': HANGZHOU,
    'ithaca': ITHACA,
    'jakarta': JAKARTA,
    'kathmandu': KATHMANDU,
    'lima': LIMA,
    'mumbai': MUMBAI,
    'nairobi': NAIROBI,
    'oxford': OXFORD,
    'paris': PARIS,
    'parisc': PARISC,
    'quebec': QUEBEC,
    'rio': RIO,
    'seoul': SEOUL,
}

protocol_version = {
    EDO: 8,
    FLORENCE: 9,
    GRANADA: 10,
    HANGZHOU: 11,
    ITHACA: 12,
    JAKARTA: 13,
    KATHMANDU: 14,
    LIMA: 15,
    MUMBAI: 16,
    NAIROBI: 17,
    OXFORD: 18,
    PARIS: 19,
    PARISC: 20,
    QUEBEC: 21,
    RIO: 22,
    SEOUL: 23,
}


sandbox_commitment = {
    "mnemonic": [
        "arctic",
        "blame",
        "brush",
        "economy",
        "solar",
        "swallow",
        "canvas",
        "live",
        "vote",
        "two",
        "post",
        "neutral",
        "spare",
        "split",
        "fall",
    ],
    "activation_code": "7375ef222cc038001b6c8fb768246c86e994745b",
    "amount": "38323962971",
    "pkh": "tz1W86h1XuWy6awbNUTRUgs6nk8q5vqXQwgk",
    "password": "ZuPOpZgMNM",
    "email": "nbhcylbg.xllfjgrk@tezos.example.org",
}

sandbox_addresses = {
    'activator': 'tz1TGu6TN5GSez2ndXXeDX6LgUDvLzPLqgYV',
    'bootstrap5': 'tz1ddb9NMYHZi5UzPdzTZMYQQZoMub195zgv',
    'bootstrap4': 'tz1b7tUupMgCNw2cCLpKTkSD1NZzB5TkP2sv',
    'bootstrap3': 'tz1faswCTDciRzE4oJ9jn2Vm2dvjeyA9fUzU',
    'bootstrap2': 'tz1gjaF81ZRRvdzjobyfVNsAeSC6PScjfQwN',
    'bootstrap1': 'tz1KqTpEZ7Yob7QbPE4Hy4Wo8fHG8LhKxZSx',
    # FIXME: Temporary, see test_sandbox.py
    'alice': 'tz1VSUr8wwNhLAzempoch5d6hLRiTh8Cjcjb',
}

# NOTE: Run `make sandbox-params` to update this file
sandbox_params = json.loads(
    Path(__file__).parent.joinpath('023-PtSeouLo-parameters', 'test-parameters.json').read_text()
)


def get_protocol_parameters(protocol_hash: str) -> Dict[str, Any]:
    return {**sandbox_params}
