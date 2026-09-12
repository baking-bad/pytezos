import json
import re
from contextlib import suppress
from os.path import dirname
from os.path import join
from typing import Any
from typing import Dict
from typing import List
from typing import Optional
from typing import Union

from attr import dataclass
from jsonschema import validate as jsonschema_validate  # type: ignore

from pytezos.context.impl import ExecutionContext
from pytezos.context.mixin import ContextMixin
from pytezos.contract import converter
from pytezos.contract import fetch_ipfs_json
from pytezos.contract import fetch_json
from pytezos.contract.view import ContractView


def _to_camelcase(string: str) -> str:
    expression = re.compile("[^A-Za-z]+")
    words = expression.split(string)
    if len(words) == 1:
        string = string[0].lower() + string[1:]
        return string
    return ''.join(w.lower() if i == 0 else w.title() for i, w in enumerate(words))


_metadata_json_replace_table = {
    '"return-type":': '"returnType":',
    '"michelson-storage-view":': '"michelsonStorageView":',
}

with open(join(dirname(__file__), 'metadata-schema.json')) as file:
    metadata_schema = json.load(file)


@dataclass(kw_only=True, frozen=True)
class StaticError:
    error: str
    expansion: str
    languages: Optional[List[str]] = None


@dataclass(kw_only=True, frozen=True)
class DynamicError:
    view: str
    languages: Optional[List[str]] = None


@dataclass(kw_only=True, frozen=True)
class License:
    name: str
    details: Optional[str] = None


@dataclass(kw_only=True, frozen=True)
class RestApiView:
    specificationUri: str
    baseUri: Optional[str] = None
    path: str
    method: Optional[str] = None


@dataclass(kw_only=True, frozen=True)
class MichelsonStorageView:
    parameter: Optional[Dict[str, Any]] = None
    returnType: Dict[str, Any]
    code: List[Any]
    annotations: Optional[List[Dict[str, Any]]] = None
    version: Optional[str] = None


@dataclass(kw_only=True, frozen=True)
class RestApiViewImplementation:
    restApiQuery: RestApiView


@dataclass(kw_only=True, frozen=True)
class MichelsonStorageViewImplementation:
    michelsonStorageView: MichelsonStorageView


@dataclass(kw_only=True, frozen=True)
class View:
    name: str
    description: Optional[str] = None
    implementations: List[Union[MichelsonStorageViewImplementation, RestApiViewImplementation]]
    pure: bool = False


@dataclass(kw_only=True, repr=False)
class ContractMetadata(ContextMixin):
    """TZIP-16 contract metadata"""

    name: Optional[str] = None
    description: Optional[str] = None
    version: Optional[str] = None
    license: Optional[License] = None
    authors: Optional[List[str]] = None
    interfaces: Optional[List[str]] = None
    errors: Optional[List[Union[StaticError, DynamicError]]] = None
    views: Optional[List[View]] = None

    def __attrs_post_init__(self) -> None:
        self.raw: Dict[str, Any] = {}
        self.storage_view_impl: Dict[str, Any] = {}
        if self.views:
            for view in self.views:
                michelson_storage_impl = next(
                    (impl for impl in view.implementations if isinstance(impl, MichelsonStorageViewImplementation)),
                    None,
                )
                if michelson_storage_impl is not None:
                    name = _to_camelcase(view.name)
                    self.storage_view_impl[name] = michelson_storage_impl.michelsonStorageView

    def __repr__(self) -> str:
        res = [
            super().__repr__(),
            '\nMetadata',
            f'.name\t\t{self.name or ""}',
            f'.description\t{self.description or ""}',
            f'.license\t{self.license.name if self.license else ""}',
            f'.authors\t{", ".join(self.authors or [])}',
            f'.interfaces\t{", ".join(self.interfaces or [])}',
            f'.errors\t\t<{len(self.errors or [])}>',
            f'.views\t\t<{len(self.views or [])}>',
            '\nStorage views',
            *list(map(lambda x: f'.{x}()', self.storage_view_impl)),
        ]
        return '\n'.join(res)

    def __getattribute__(self, name: str) -> ContractView:
        with suppress(AttributeError):
            return super().__getattribute__(name)
        try:
            impl = self.storage_view_impl[name]
            return ContractView(
                context=self.context,
                name=name,
                parameter=impl.parameter,
                return_type=impl.returnType,
                code=impl.code,
            )
        except KeyError as e:
            raise KeyError(f'Unknown view `{name}`, available: {list(self.storage_view_impl.keys())}') from e

    def __call__(self) -> dict:
        return self.raw

    # FIXME: Unnecessary multiple JSON conversions
    @staticmethod
    def fix_metadata_json(metadata_json: Dict[str, Any]) -> Dict[str, Any]:
        """Fix invalid field casing in metadata JSON"""
        metadata_json_string = json.dumps(metadata_json)
        for from_, to in _metadata_json_replace_table.items():
            metadata_json_string = metadata_json_string.replace(from_, to)
        return json.loads(metadata_json_string)

    @staticmethod
    def validate_metadata_json(metadata_json: Dict[str, Any]) -> None:
        """Validate metadata JSON with JSONSchema"""
        jsonschema_validate(instance=metadata_json, schema=metadata_schema)

    @classmethod
    def from_json(cls, metadata_json: Dict[str, Any], context: Optional[ExecutionContext] = None) -> 'ContractMetadata':
        """Convert metadata from JSON object"""
        metadata_json = cls.fix_metadata_json(metadata_json)
        cls.validate_metadata_json(metadata_json)
        res = converter.structure(metadata_json, ContractMetadata)
        res.context = context if context else ExecutionContext()
        res.raw = metadata_json
        return res

    @classmethod
    def from_ipfs(cls, multihash: str, context: Optional[ExecutionContext] = None) -> 'ContractMetadata':
        """Fetch metadata from IPFS network by multihash"""
        context = context or ExecutionContext()
        metadata_json = fetch_ipfs_json(multihash, context.ipfs_gateway)
        return cls.from_json(metadata_json, context)

    @classmethod
    def from_url(cls, url: str, context: Optional[ExecutionContext] = None) -> 'ContractMetadata':
        """Fetch metadata from HTTP(S) URL"""
        metadata_json = fetch_json(url)
        return cls.from_json(metadata_json, context)

    @classmethod
    def from_file(cls, path: str, context: Optional[ExecutionContext] = None) -> 'ContractMetadata':
        """Read metadata from JSON file by path"""
        with open(path) as f:
            metadata_json = json.load(f)
            return cls.from_json(metadata_json, context)
