"""In-process stand-in for a Tezos X Michelson sequencer.

The Tezos X Michelson L2 (Tezlink runtime inside `octez-evm-node`) speaks the regular
Tezos node RPC, with one structural difference: there is no mempool, so every
`/chains/main/mempool/*` route except `filter` answers 404, and the fee filter it
does serve carries sub-mainnet thresholds. This stub reproduces exactly that surface
by patching `requests.request` — the single choke point of `pytezos.rpc.node.RpcNode` —
so unit tests run against it without network or Docker.

Responses below are shaped after live answers of
https://michelson.previewnet.tezosx.nomadic-labs.com (recorded 2026-09-04).
"""

import json
from typing import Any
from typing import Callable
from typing import Dict
from typing import List
from typing import Optional
from typing import Tuple
from unittest.mock import patch

import requests

STUB_URL = 'http://tezosx-stub'

# Live previewnet values: per-byte 4x above mainnet defaults, per-gas below them.
PREVIEWNET_MEMPOOL_FILTER = {
    'minimal_fees': '100',
    'minimal_nanotez_per_gas_unit': ['45', '1'],
    'minimal_nanotez_per_byte': ['4000', '1'],
    'replace_by_fee_factor': ['21', '20'],
}

CHAIN_ID = 'NetXY2oPPzkxUW1'
PROTOCOL = 'PsUshuai9QapM5TGj1JpuVGkdxz5GykdnEvS6Rh8SUVrARvZLCY'
HEAD_HASH = 'BLq3T9jDqCG1eHvMLqugGYK6xjFc9ht71X7SiRBWdKAwKyu7p7o'
OLD_HASH = 'BLPg4GtCSC5sdenBGnr1V7ritJpp5uVZTnNabVk1pRb76zW1WqH'
HEAD_LEVEL = 734852

Handler = Callable[[str, str, Dict[str, Any]], Tuple[int, Any]]


def _json_response(status: int, body: Any, url: str) -> requests.Response:
    res = requests.Response()
    res.status_code = status
    res.url = url
    if body is None:
        res._content = b''  # the sequencer answers 404 with an empty body
    else:
        res._content = json.dumps(body).encode()
        res.headers['content-type'] = 'application/json'
    return res


class SequencerStub:
    """Context manager that answers pytezos RPC calls like a Tezos X sequencer would.

    Usage::

        with SequencerStub() as node:
            client = pytezos.using(shell=STUB_URL, key=...)
            ...
            node.calls  # [(method, path), ...] for assertions
    """

    def __init__(self, extra_routes: Optional[Dict[str, Any]] = None, mempool_filter: Optional[dict] = None):
        self.calls: List[Tuple[str, str]] = []
        self.mempool_filter = mempool_filter or PREVIEWNET_MEMPOOL_FILTER
        self.routes: Dict[str, Any] = self._default_routes()
        if extra_routes:
            self.routes.update(extra_routes)
        self._patcher = patch('pytezos.rpc.node.requests.request', side_effect=self._handle)

    # --- routes --------------------------------------------------------------

    def _default_routes(self) -> Dict[str, Any]:
        header = {
            'protocol': PROTOCOL,
            'chain_id': CHAIN_ID,
            'hash': HEAD_HASH,
            'level': HEAD_LEVEL,
            'predecessor': OLD_HASH,
            'timestamp': '2026-09-04T03:44:53Z',
        }
        constants = {
            'minimal_block_delay': '1',
            'hard_gas_limit_per_operation': '660000',
            'hard_storage_limit_per_operation': '60000',
            'cost_per_byte': '1',
            'origination_size': 257,
        }
        routes: Dict[str, Any] = {
            '/version': {
                'version': {'major': 0, 'minor': 65, 'build': 0, 'additional_info': 'release'},
                'network_version': {'chain_name': 'TEZOS_PREVIEWNET_TEZOSX_Chain_id (1507644015)'},
            },
            '/chains/main/chain_id': CHAIN_ID,
            '/chains/main/mempool/filter': self.mempool_filter,
            # No mempool on the sequencer: pending_operations / monitor_operations 404 (see fallback in _handle)
            '/chains/main/blocks/head/hash': HEAD_HASH,
            '/chains/main/blocks/head/header': header,
            '/chains/main/blocks/head/protocols': {'protocol': PROTOCOL, 'next_protocol': PROTOCOL},
            '/chains/main/blocks/head/context/constants': constants,
            '/chains/main/blocks/head/helpers/scripts/run_operation': self._run_operation,
            '/injection/operation': 'ooStubInjectedOperationHash',
        }
        for block in (HEAD_HASH, OLD_HASH):
            routes[f'/chains/main/blocks/{block}/hash'] = block
            routes[f'/chains/main/blocks/{block}/header'] = header
            routes[f'/chains/main/blocks/{block}/context/constants'] = constants
        for offset in range(0, 121):
            routes[f'/chains/main/blocks/head~{offset}/hash'] = OLD_HASH
        return routes

    def add_account(self, pkh: str, balance: int = 10_000_000, counter: int = 0) -> None:
        base = f'/chains/main/blocks/head/context/contracts/{pkh}'
        self.routes[base] = {'balance': str(balance), 'counter': str(counter)}
        self.routes[base + '/counter'] = str(counter)
        self.routes[base + '/manager_key'] = None if counter == 0 else 'edpk-stub'

    @staticmethod
    def _run_operation(method: str, path: str, kwargs: Dict[str, Any]) -> Tuple[int, Any]:
        """Echo the operation back as `applied`, the way run_operation does for a valid op."""
        operation = kwargs['json']['operation']
        contents = []
        for content in operation['contents']:
            contents.append(
                {
                    **content,
                    'metadata': {
                        'operation_result': {
                            'status': 'applied',
                            'consumed_milligas': '168420',
                        }
                    },
                }
            )
        return 200, {**operation, 'contents': contents}

    # --- plumbing --------------------------------------------------------------

    def _handle(self, method: str, url: str, **kwargs: Any) -> requests.Response:
        assert url.startswith(STUB_URL), url
        path = url[len(STUB_URL) :].split('?')[0].rstrip('/')
        self.calls.append((method, path))
        if path not in self.routes:
            return _json_response(404, None, url)
        route = self.routes[path]
        if callable(route):
            status, body = route(method, path, kwargs)
            return _json_response(status, body, url)
        return _json_response(200, route, url)

    def __enter__(self) -> 'SequencerStub':
        self._patcher.start()
        return self

    def __exit__(self, *exc: Any) -> None:
        self._patcher.stop()

    def count(self, path_suffix: str) -> int:
        return sum(1 for _, path in self.calls if path.endswith(path_suffix))
