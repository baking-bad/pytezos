from contextlib import suppress
from datetime import datetime
from datetime import timezone
from typing import Any
from typing import Dict
from typing import Type

import dateutil.parser
import requests
from cattr import Converter


def structure_datetime(obj: Any, cls: Type) -> datetime:
    with suppress(ValueError, TypeError):
        return datetime.utcfromtimestamp(float(obj)).replace(tzinfo=timezone.utc)
    with suppress(dateutil.parser.ParserError):
        return dateutil.parser.parse(obj)
    raise ValueError


def unstructure_datetime(obj: datetime) -> float:
    return obj.timestamp()


converter = Converter()
converter.register_structure_hook(datetime, structure_datetime)
converter.register_unstructure_hook(datetime, unstructure_datetime)


def fetch_json(url: str) -> Dict[str, Any]:
    """Fetch a JSON document over HTTP(S), raising :class:`requests.HTTPError` on a non-2xx response"""
    res = requests.get(url, timeout=60)
    res.raise_for_status()
    return res.json()


def fetch_ipfs_json(multihash: str, ipfs_gateway: str) -> Dict[str, Any]:
    """Fetch a JSON document from IPFS through an HTTP gateway

    :param multihash: IPFS content identifier
    :param ipfs_gateway: gateway base URI, e.g. ``https://ipfs.filebase.io/ipfs``
    :raises requests.RequestException: if the gateway is unreachable, answers non-2xx or serves non-JSON
    """
    try:
        return fetch_json(f'{ipfs_gateway}/{multihash}')
    except requests.RequestException as e:
        raise requests.RequestException(
            f'IPFS gateway `{ipfs_gateway}` failed to serve `{multihash}`: {e}; '
            'set another gateway with `pytezos.using(ipfs_gateway=...)`',
            response=e.response,
            request=e.request,
        ) from e
