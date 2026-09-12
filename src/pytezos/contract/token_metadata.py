import json
from datetime import datetime
from datetime import time
from os.path import dirname
from os.path import join
from typing import Any
from typing import Dict
from typing import List
from typing import Optional

from attr import dataclass
from jsonschema import validate as jsonschema_validate  # type: ignore

from pytezos.context.impl import ExecutionContext
from pytezos.context.mixin import ContextMixin
from pytezos.contract import converter
from pytezos.contract import fetch_ipfs_json
from pytezos.contract import fetch_json

with open(join(dirname(__file__), 'token_metadata-schema.json')) as file:
    token_metadata_schema = json.load(file)

# NOTE: "time" is a format not a type
token_metadata_schema['definitions']['format']['properties']['duration']['type'] = "string"
token_metadata_schema['definitions']['asset']['properties']['name'] = {'type': 'string'}
token_metadata_schema['definitions']['asset']['properties']['symbol'] = {'type': 'string'}
token_metadata_schema['definitions']['asset']['properties']['decimals'] = {'type': 'integer'}


@dataclass(kw_only=True, frozen=True)
class Attribute:
    name: str
    value: str
    type: Optional[str] = None


@dataclass(kw_only=True, frozen=True)
class Dimensions:
    value: str
    unit: str


@dataclass(kw_only=True, frozen=True)
class DataRate:
    value: str
    unit: str


@dataclass(kw_only=True, frozen=True)
class Format:
    uri: Optional[str] = None
    hash: Optional[str] = None
    mimeType: Optional[str] = None
    fileSize: Optional[int] = None
    fileName: Optional[str] = None
    duration: Optional[time] = None
    dimensions: Optional[Dimensions] = None
    dataRate: Optional[DataRate] = None


@dataclass(kw_only=True)
class ContractTokenMetadata(ContextMixin):
    """TZIP-21 token metadata"""

    name: Optional[str] = None
    symbol: Optional[str] = None
    decimals: int

    # Fungible Token Recommendations
    symbolPreference: Optional[str] = None
    thumbnailUri: Optional[str] = None

    # Semi-fungible and NFT Token Recommendations
    artifactUri: Optional[str] = None
    displayUri: Optional[str] = None
    description: Optional[str] = None
    minter: Optional[str] = None
    creators: Optional[List[str]] = None
    isBooleanAmount: Optional[bool] = None

    # Multimedia NFT Token Recommendations
    formats: Optional[List[Format]] = None
    tags: Optional[List[str]] = None

    contributors: Optional[List[str]] = None
    publishers: Optional[List[str]] = None
    date: Optional[datetime] = None
    blockLevel: Optional[int] = None
    type: Optional[str] = None
    genres: Optional[List[str]] = None
    language: Optional[List[str]] = None
    identifier: Optional[str] = None
    rights: Optional[str] = None
    rightsUri: Optional[str] = None
    externalUri: Optional[str] = None
    isTransferable: Optional[bool] = None
    shouldPreferSymbol: Optional[str] = None
    attributes: Optional[List[Attribute]] = None
    assets: Optional[List['ContractTokenMetadata']] = None

    def __attrs_post_init__(self):
        self.raw = {}
        self.storage_view_impl = {}

    @staticmethod
    def validate_token_metadata_json(metadata_json: Dict[str, Any]) -> None:
        """Validate token metadata JSON with JSONSchema"""
        jsonschema_validate(instance=metadata_json, schema=token_metadata_schema)

    @classmethod
    def from_json(
        cls,
        token_metadata_json: Dict[str, Any],
        context: Optional[ExecutionContext] = None,
    ) -> 'ContractTokenMetadata':
        """Convert token metadata from JSON object"""

        for key, value in token_metadata_json.items():
            if isinstance(value, bytes):
                token_metadata_json[key] = value.decode()
        if 'decimals' in token_metadata_json:
            token_metadata_json['decimals'] = int(token_metadata_json['decimals'])

        cls.validate_token_metadata_json(token_metadata_json)
        res = converter.structure(token_metadata_json, ContractTokenMetadata)
        res.context = context if context else ExecutionContext()
        res.raw = token_metadata_json
        return res

    @classmethod
    def from_ipfs(cls, multihash: str, context: Optional[ExecutionContext] = None) -> 'ContractTokenMetadata':
        """Fetch token metadata from IPFS network by multihash"""
        context = context or ExecutionContext()
        token_metadata_json = fetch_ipfs_json(multihash, context.ipfs_gateway)
        return cls.from_json(token_metadata_json, context)

    @classmethod
    def from_url(cls, url: str, context: Optional[ExecutionContext] = None) -> 'ContractTokenMetadata':
        """Fetch token metadata from HTTP(S) URL"""
        token_metadata_json = fetch_json(url)
        return cls.from_json(token_metadata_json, context)

    @classmethod
    def from_file(cls, path: str, context: Optional[ExecutionContext] = None) -> 'ContractTokenMetadata':
        """Read token metadata from JSON file by path"""
        with open(path) as f:
            token_metadata_json = json.load(f)
            return cls.from_json(token_metadata_json, context)
