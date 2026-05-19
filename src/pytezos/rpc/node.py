import json
from pprint import pformat
from time import sleep
from typing import Any
from typing import Dict
from typing import List
from typing import Optional
from typing import Union

import requests
import requests.exceptions
from simplejson import JSONDecodeError

from pytezos.logging import logger

# Octez occasionally returns 500 with `kind: temporary` for endpoints that
# touch the prevalidator while a block is being baked (mempool.pending_operations
# at prevalidator.ml:1918, etc.). Retry such responses a few times with a small
# backoff — `temporary` is octez's own signal that the error is transient.
TRANSIENT_RETRY_ATTEMPTS = 6
TRANSIENT_RETRY_INITIAL_DELAY = 0.25
TRANSIENT_RETRY_MAX_DELAY = 2.0


def _urljoin(*args: str) -> str:
    return "/".join(map(lambda x: str(x).strip('/'), args))


_TRANSIENT_TEXT_MARKERS = ('prevalidator.ml',)  # mempool assertions during concurrent baking


def _is_transient_response(res: requests.Response) -> bool:
    """Check whether a non-2xx response is a transient octez infrastructure
    error (mempool/prevalidator hiccups, etc.). Protocol-level errors
    (id starting with `proto.`) are NOT retried even if octez marks them
    `kind: temporary` — those are domain failures like `michelson_v1.*`."""
    if res.headers.get('content-type') == 'application/json':
        try:
            body = res.json()
        except (ValueError, JSONDecodeError):
            body = None
        if isinstance(body, list):
            if any(isinstance(err, dict) and err.get('id', '').startswith('proto.') for err in body):
                return False
            if any(isinstance(err, dict) and err.get('kind') == 'temporary' for err in body):
                return True
    return any(marker in res.text for marker in _TRANSIENT_TEXT_MARKERS)


def _gen_error_variants(error_id: str) -> List[str]:
    chunks = error_id.split('.')
    variants = [error_id]
    if len(chunks) > 1:
        variants.append(chunks[-2])
        if len(chunks) > 2:
            variants.append('.'.join(chunks[2:]))
    return variants


class RpcError(Exception):
    __handlers__ = {}  # type: ignore

    @classmethod
    def __init_subclass__(cls, error_id: Union[str, List[str]]) -> None:
        super().__init_subclass__()
        if isinstance(error_id, list):
            for eid in error_id:
                cls.__handlers__[eid] = cls
        else:
            cls.__handlers__[error_id] = cls

    @classmethod
    def from_errors(cls, errors: List[Dict[str, Any]]) -> 'RpcError':
        """Create RpcError from "errors" section of response JSON."""
        if not errors:
            return RpcError('Unspecified error')

        # FIXME: Only first error is being processed
        error = errors[-1]
        for key in _gen_error_variants(error['id']):
            if key in cls.__handlers__:
                handler = cls.__handlers__[key]
                return handler(error)
        return RpcError(error)

    @classmethod
    def from_response(cls, res: requests.Response) -> 'RpcError':
        """Create RpcError from requests Response."""
        if res.headers.get('content-type') == 'application/json':
            try:
                errors = res.json()
            except JSONDecodeError:
                # sometimes rpc returns invalid json
                return RpcError(res.text)
            assert isinstance(errors, list)
            return cls.from_errors(errors)
        else:
            return RpcError(res.text)

    def __str__(self) -> str:
        return pformat(self.args)


class RpcNode:
    """Request proxy for a single Tezos node."""

    def __init__(self, uri: Union[str, List[str]], headers: Optional[Dict[str, str]] = None) -> None:
        if not uri:
            raise RuntimeError()
        if not isinstance(uri, list):
            uri = [uri]
        self.uri = uri
        self.headers = headers or {}

    def __repr__(self) -> str:
        res = [
            super().__repr__(),
            '\nNode address',
            self.uri[0],
        ]
        return '\n'.join(res)

    def request(self, method: str, path: str, **kwargs) -> requests.Response:
        """Perform HTTP request to node.

        :param method: one of GET/POST/PUT/DELETE
        :param path: path to endpoint
        :param kwargs: requests.request arguments
        :raises RpcError: node has returned an error
        :returns: node response
        """
        logger.debug('>>>>> %s %s\n%s', method, path, json.dumps(kwargs, indent=4))
        timeout = kwargs.pop('timeout', None) or 60
        delay = TRANSIENT_RETRY_INITIAL_DELAY
        for attempt in range(TRANSIENT_RETRY_ATTEMPTS):
            res = requests.request(
                method=method,
                url=_urljoin(self.uri[0], path),
                headers={'content-type': 'application/json', 'user-agent': 'PyTezos', **self.headers},
                timeout=timeout,
                **kwargs,
            )
            if res.status_code >= 500 and _is_transient_response(res) and attempt < TRANSIENT_RETRY_ATTEMPTS - 1:
                logger.debug('transient %s on %s %s, retrying in %.2fs', res.status_code, method, path, delay)
                sleep(delay)
                delay = min(delay * 2, TRANSIENT_RETRY_MAX_DELAY)
                continue
            break
        if res.status_code == 401:
            logger.debug('<<<<< %s\n%s', res.status_code, res.text)
            raise RpcError(f'Unauthorized: {path}')
        if res.status_code == 404:
            logger.debug('<<<<< %s\n%s', res.status_code, res.text)
            raise RpcError(f'Not found: {path}')
        if res.status_code != 200:
            logger.debug('<<<<< %s\n%s', res.status_code, pformat(res.text, indent=4))
            raise RpcError.from_response(res)

        logger.debug('<<<<< %s\n%s', res.status_code, json.dumps(res.json(), indent=4))
        return res

    def get(
        self,
        path: str,
        params: Optional[Dict[str, Any]] = None,
        timeout: Optional[int] = None,
    ) -> requests.Response:
        return self.request(
            'GET',
            path,
            params=params,
            timeout=timeout,
        ).json()

    def post(
        self,
        path: str,
        params: Optional[Dict[str, Any]] = None,
        json=None,
        timeout: Optional[int] = None,
    ) -> Union[requests.Response, str]:
        response = self.request(
            'POST',
            path,
            params=params,
            json=json,
            timeout=timeout,
        )
        try:
            return response.json()
        except JSONDecodeError:
            return response.text

    def delete(
        self,
        path: str,
        params: Optional[Dict[str, Any]] = None,
        timeout: Optional[int] = None,
    ) -> requests.Response:
        return self.request(
            'DELETE',
            path,
            params=params,
            timeout=timeout,
        ).json()

    def put(
        self,
        path: str,
        params: Optional[Dict[str, Any]] = None,
        timeout: Optional[int] = None,
    ) -> requests.Response:
        return self.request(
            'PUT',
            path,
            params=params,
            timeout=timeout,
        ).json()


class RpcMultiNode(RpcNode):
    """Request proxy for multiple nodes chosen for each request in round-robin order."""

    def __init__(self, uri: Union[str, List[str]]) -> None:
        super().__init__(uri)
        self.nodes = list(map(RpcNode, self.uri))
        self._next_i = 0

    def __repr__(self) -> str:
        res = [
            super().__repr__(),
            '\nNode addresses',
            *self.uri,
        ]
        return '\n'.join(res)

    def request(self, method: str, path: str, **kwargs) -> requests.Response:
        assert self._next_i < len(self.nodes)
        res = self.nodes[self._next_i].request(method, path, **kwargs)
        self._next_i = (self._next_i + 1) % len(self.nodes)
        return res
