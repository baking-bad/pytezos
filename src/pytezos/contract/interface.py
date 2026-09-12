import json
import logging
import warnings
from decimal import Decimal
from functools import cached_property
from functools import lru_cache
from os.path import exists
from os.path import expanduser
from typing import Any
from typing import Callable
from typing import Dict
from typing import Generic
from typing import Iterator
from typing import List
from typing import Optional
from typing import Type
from typing import TypeVar
from typing import Union
from typing import cast
from urllib.parse import urlparse

import requests
from deprecation import deprecated  # type: ignore

from pytezos.context.mixin import ContextMixin
from pytezos.context.mixin import ExecutionContext
from pytezos.contract.data import ContractData
from pytezos.contract.entrypoint import ContractEntrypoint
from pytezos.contract.metadata import ContractMetadata
from pytezos.contract.result import ContractCallResult
from pytezos.contract.token_metadata import ContractTokenMetadata
from pytezos.contract.view import ContractView
from pytezos.crypto.key import Key
from pytezos.jupyter import get_class_docstring
from pytezos.logging import logger
from pytezos.michelson.format import micheline_to_michelson
from pytezos.michelson.micheline import MichelsonRuntimeError
from pytezos.michelson.parse import michelson_to_micheline
from pytezos.michelson.program import MichelsonProgram
from pytezos.michelson.sections import ViewSection
from pytezos.michelson.types import BigMapType
from pytezos.michelson.types import BytesType
from pytezos.michelson.types.base import generate_pydoc
from pytezos.operation.group import OperationGroup
from pytezos.rpc import ShellQuery


class ContractTokenMetadataProxy:
    """Get TZIP-21 contract token metadata by token_id"""

    def __init__(self, fn: Callable) -> None:
        self._fn = fn

    def __getitem__(self, item):
        return self._fn(item)


T = TypeVar('T', ContractEntrypoint, ContractView)


class ContractProxyNamespace(Generic[T]):
    """Entrypoint or view proxies by name: `contract.entrypoint.<name>` / `contract.view.<name>`

    Holds every proxy of the contract, including those whose names collide with `ContractInterface` attributes
    (e.g. `storage`, `metadata`, `token_metadata`) or with each other (an entrypoint and a view sharing a name).
    Names that are not Python identifiers are reachable via item access: `contract.entrypoint['foo.bar']`.
    """

    def __init__(self, title: str, proxies: Dict[str, T]) -> None:
        self._title = title
        self._proxies: Dict[str, T] = proxies

    def __repr__(self) -> str:
        res = [
            super().__repr__(),
            f'\n{self._title.capitalize()}s',
            *(f'.{name}()' for name in self._proxies),
        ]
        return '\n'.join(res)

    def __getattr__(self, name: str) -> T:
        if name.startswith('_'):
            raise AttributeError(name)
        try:
            return self._proxies[name]
        except KeyError:
            raise AttributeError(f'unknown {self._title} `{name}`, available: {list(self._proxies)}') from None

    def __getitem__(self, name: str) -> T:
        return self._proxies[name]

    def __contains__(self, name: object) -> bool:
        return name in self._proxies

    def __iter__(self) -> Iterator[str]:
        return iter(self._proxies)

    def __len__(self) -> int:
        return len(self._proxies)

    def __dir__(self) -> List[str]:
        return [*super().__dir__(), *self._proxies]


class ContractInterface(ContextMixin):
    """Proxy class for interacting with a contract.

    Entrypoints and views are exposed as `.<name>()` shortcuts when the name is free, and always as
    `.entrypoint.<name>()` / `.view.<name>()`. An entrypoint wins over a view of the same name, and both lose
    to an existing interface attribute such as `storage`, `metadata` or `token_metadata`.
    """

    program: MichelsonProgram
    entrypoint: ContractProxyNamespace[ContractEntrypoint]  #: every entrypoint proxy by name
    view: ContractProxyNamespace[ContractView]  #: every on-chain view proxy by name

    def __init__(self, context: ExecutionContext) -> None:
        super().__init__(context=context)
        self._logger = logging.getLogger(__name__)
        self._storage: Optional[ContractData] = None
        self.entrypoints = self.program.parameter.list_entrypoints()
        self.views = {view.name: view for view in self.program.views}  # type: Dict[str, Type[ViewSection]]

        entrypoints: Dict[str, ContractEntrypoint] = {}
        for entrypoint, ty in self.entrypoints.items():
            attr = ContractEntrypoint(context=context, entrypoint=entrypoint)
            attr.__doc__ = generate_pydoc(ty, entrypoint)
            entrypoints[entrypoint] = attr

        views: Dict[str, ContractView] = {}
        for view_name, view_ty in self.views.items():
            view_attr = ContractView(
                context=context,
                name=view_name,
                parameter=view_ty.args[1].as_micheline_expr(),
                return_type=view_ty.args[2].as_micheline_expr(),
                code=view_ty.args[3].as_micheline_expr(),  # type: ignore
            )
            view_attr.__doc__ = view_ty.generate_pydoc()  # type: ignore
            views[view_name] = view_attr

        self.entrypoint = ContractProxyNamespace('entrypoint', entrypoints)
        self.view = ContractProxyNamespace('view', views)

        for name, attr in entrypoints.items():
            self._bind_shortcut('entrypoint', name, attr)
        for name, view_attr in views.items():
            self._bind_shortcut('view', name, view_attr)

    def _bind_shortcut(self, title: str, name: str, proxy: Union[ContractEntrypoint, ContractView]) -> None:
        if name in vars(self) or hasattr(type(self), name):
            if name != 'token_metadata':  # legacy TZIP-12 entrypoint: `.token_metadata` is the TZIP-21 proxy by design
                warnings.warn(f'`.{name}` is reserved, use `.{title}.{name}` instead', stacklevel=3)
        else:
            setattr(self, name, proxy)

    def _list_namespace(self, namespace: ContractProxyNamespace) -> Iterator[str]:
        for name in namespace:
            if vars(self).get(name) is namespace[name]:
                yield f'.{name}()'
            else:
                yield f'.{namespace._title}.{name}()'

    def __repr__(self) -> str:
        res = [
            super().__repr__(),
            '.storage\t# access storage data at block `block_id`',
            '.parameter\t# root entrypoint',
            '.entrypoint\t# entrypoints by name',
            '.view\t\t# views by name',
            '\nEntrypoints',
            *self._list_namespace(self.entrypoint),
            '\nViews',
            *self._list_namespace(self.view),
            '\nHelpers',
            get_class_docstring(self.__class__, attr_filter=lambda x: x not in self.entrypoints),
        ]
        return '\n'.join(res)

    def __getattr__(self, item: str) -> ContractEntrypoint:
        raise AttributeError(f'unexpected entrypoint {item}, use `.entrypoint.<name>` / `.view.<name>`')

    @staticmethod
    def from_url(url: str, context: Optional[ExecutionContext] = None) -> 'ContractInterface':
        """Create contract from michelson source code available via URL

        :param url: link to the Michelson file
        :param context: optional execution context
        :rtype: ContractInterface
        """
        res = requests.get(url, timeout=60)
        if res.status_code != 200:
            raise ValueError(f'cannot fetch `{url} {res.status_code}`', res.text)
        return ContractInterface.from_michelson(res.text, context)

    @staticmethod
    def from_file(path: str, context: Optional[ExecutionContext] = None) -> 'ContractInterface':
        """Create contract from michelson source code stored in a file.

        :param path: Path to the `.tz` file
        :param context: optional execution context
        :rtype: ContractInterface
        """
        with open(expanduser(path)) as f:
            return ContractInterface.from_michelson(f.read(), context)

    @staticmethod
    def from_michelson(source: str, context: Optional[ExecutionContext] = None) -> 'ContractInterface':
        """Create contract from michelson source code.

        :param source: Michelson source code
        :param context: optional execution context
        :rtype: ContractInterface
        """
        return ContractInterface.from_micheline(michelson_to_micheline(source), context)

    @staticmethod
    def from_micheline(
        expression: List[Dict[str, Any]],
        context: Optional[ExecutionContext] = None,
    ) -> 'ContractInterface':
        """Create contract from micheline expression.

        :param expression: [{'prim': 'parameter'}, {'prim': 'storage'}, {'prim': 'code'}]
        :param context: optional execution context
        :rtype: ContractInterface
        """
        if context is not None:
            code_expr = context.resolve_global_constants(expression)
        else:
            code_expr = expression
        program = MichelsonProgram.match(code_expr)
        cls = type(ContractInterface.__name__, (ContractInterface,), {'program': program})
        context = ExecutionContext(
            shell=context.shell if context else None,
            key=context.key if context else None,
            script={'code': code_expr},
            global_constants=context.global_constants if context else None,
        )
        return cls(context)

    @staticmethod
    def from_context(context: ExecutionContext) -> 'ContractInterface':
        """Create contract from the previously loaded context data.

        :param context: execution context
        :return: ContractInterface
        """
        program = MichelsonProgram.load(context, with_code=True)
        cls = type(ContractInterface.__name__, (ContractInterface,), {'program': program})
        return cls(context)

    @classmethod
    @deprecated(
        deprecated_in='3.0.0',
        removed_in='4.0.0',
        details='use one of `from_file`, `from_michelson`, `from_micheline`, `from_url`',
    )
    def create_from(cls, source):
        """Create contract interface from its code.

        :param source: Michelson code, filename, or Micheline JSON
        :rtype: ContractInterface
        """
        if isinstance(source, str):
            if exists(expanduser(source)):
                return ContractInterface.from_file(source)
            return ContractInterface.from_michelson(source)
        return ContractInterface.from_micheline(source)

    def to_micheline(self) -> List[Dict[str, Any]]:
        """Get contract script in Micheline JSON

        :return:  [{'prim': 'parameter'}, {'prim': 'storage'}, {'prim': 'code'}]
        """
        return self.program.as_micheline_expr()

    def to_michelson(self) -> str:
        """Get contract listing in formatted Michelson

        :return: string
        """
        return micheline_to_michelson(self.to_micheline())

    def to_file(self, path: str) -> None:
        """Write contract source to a .tz file

        :param path: path to the file
        """
        with open(path, 'w+') as f:
            f.write(self.to_michelson())

    @deprecated(deprecated_in='3.0.0', removed_in='4.0.0', details='use `.storage[path][to][big_map][key]()` instead')
    def big_map_get(self, path):
        """Get BigMap entry as Python object by plain key and block height.

        :param path: JSON path to the key (or just key to access default BigMap location).
            Use `/` to separate nodes and `::` to separate tuple args.
            In any other case you'd need to escape those symbols.
        :returns: object
        """
        node = self.storage
        for item in path.split('/'):
            if len(item) == 0:
                continue
            if isinstance(item, str):
                res = item.split('::')
                item = tuple(res) if len(res) > 1 else item
            node = node[item]
        return node() if node else None

    def using(
        self,
        shell: Optional[Union[ShellQuery, str]] = None,
        key: Optional[Union[Key, str]] = None,
        block_id: Optional[Union[str, int]] = None,
        mode: Optional[str] = None,
        ipfs_gateway: Optional[str] = None,
    ) -> 'ContractInterface':
        """Change the block at which the current contract is inspected.

        Also, if address is undefined you can specify RPC endpoint, and private key.

        :param shell: one of 'mainnet', '***net', or RPC node uri, or instance of :class:`pytezos.rpc.shell.ShellQuery`
        :param key: base58 encoded key, path to the faucet file, alias from tezos-client, or instance of `Key`
        :param block_id: block height / hash / offset to use, default is `head`
        :param mode: whether to use `readable` or `optimized` encoding for parameters/storage/other
        :param ipfs_gateway: override IPFS gateway URI
        :rtype: ContractInterface
        """
        has_address = self.context.address is not None
        return type(self)(
            self._spawn_context(
                shell=None if has_address else shell,
                key=None if has_address else key,
                address=self.context.address,
                block_id=block_id,
                mode=mode,
                ipfs_gateway=ipfs_gateway,
            )
        )

    @property
    def storage(self) -> ContractData:
        if self._storage:
            return self._storage
        elif self.address:
            expr = self.shell.blocks[self.context.block_id].context.contracts[self.address].storage()
            storage = self.program.storage.from_micheline_value(expr)
            storage.attach_context(self.context)
        else:
            storage = self.program.storage.dummy(self.context)
        return ContractData(self.context, storage.item, title="storage")

    @storage.setter
    def storage(self, storage: ContractData) -> None:
        if self.address:
            raise Exception('Can\'t set storage of deployed contract')
        self._storage = storage

    def storage_from_file(self, path: str) -> None:
        """Load contract storage from file

        :param path: path to .tz file
        """
        with open(path) as file:
            expr = michelson_to_micheline(file.read())
        self.storage_from_micheline(expr)

    def storage_from_micheline(self, expression) -> None:
        """Load contract storage from Micheline expression

        :param expression: Micheline expression
        """
        storage = self.program.storage.from_micheline_value(expression)
        storage.attach_context(self.context)
        self.storage = ContractData(self.context, storage.item, title="storage")

    def storage_from_michelson(self, source: str) -> None:
        """Load contract storage from Michelson code

        :param source: Michelson code
        """
        expr = michelson_to_micheline(source)
        self.storage_from_micheline(expr)

    @cached_property
    def metadata(self) -> Optional[ContractMetadata]:
        """Get TZIP-016 contract metadata, if exists

        :rtype: ContractMetadata
        """
        metadata_url = self.metadata_url
        if metadata_url is None:
            return None

        logger.info('Trying to fetch contract metadata from `%s`', metadata_url)
        parsed_url = urlparse(metadata_url)

        if parsed_url.scheme in ('http', 'https'):
            # NOTE: KT1B34qXVRfQrScEaqjjt6cJ5G8LtVFZ7fSc
            metadata = ContractMetadata.from_url(metadata_url, self.context)

        elif parsed_url.scheme == 'ipfs':
            # NOTE: KT1AFA2mwNUMNd4SsujE1YYp29vd8BZejyKW
            metadata = ContractMetadata.from_ipfs(parsed_url.netloc, self.context)

        elif parsed_url.scheme == 'tezos-storage':
            parts = parsed_url.path.split('/')
            if len(parts) == 1:
                # NOTE: KT1JBThDEqyqrEHimhxoUBCSnsKAqFcuHMkP
                storage = self.storage
            elif len(parts) == 2:
                # NOTE: KT1REEb5VxWRjcHm5GzDMwErMmNFftsE5Gpf
                context = self._spawn_context(address=parsed_url.netloc)
                storage = ContractInterface.from_context(context).storage
            else:
                raise NotImplementedError('Unknown metadata URL scheme')
            metadata_json = json.loads(storage['metadata'][parts[-1]]().decode())
            metadata = ContractMetadata.from_json(metadata_json, self.context)

        elif parsed_url.scheme == 'sha256':
            raise NotImplementedError

        else:
            raise NotImplementedError('Unknown metadata URL scheme')

        return metadata

    @property
    def token_metadata(self) -> ContractTokenMetadataProxy:
        """Get TZIP-021 contract token metadata proxy

        :rtype: ContractTokenMetadataProxy
        """
        return ContractTokenMetadataProxy(self._get_token_metadata)  # type: ignore

    @lru_cache(maxsize=1000)  # noqa: B019
    def _get_token_metadata(self, token_id: int) -> Optional[ContractTokenMetadata]:
        token_metadata = self._get_token_metadata_from_view(token_id)
        if token_metadata is None:
            token_metadata = self._get_token_metadata_from_storage(token_id)
        return token_metadata

    def _get_token_metadata_from_storage(self, token_id: int) -> Optional[ContractTokenMetadata]:
        self._logger.info('Trying to fetch token %s metadata from storage', token_id)
        try:
            token_metadata_url = self.storage['token_metadata'][token_id]['token_info']['']().decode()
        # FIXME: Dirty
        except (KeyError, AssertionError):
            self._logger.info('Storage doesn\'t contain metadata URL for token %s', token_id)
            return None

        self._logger.info('Trying to fetch contract token metadata from `%s`', token_metadata_url)
        parsed_url = urlparse(token_metadata_url)

        if parsed_url.scheme in ('http', 'https'):
            token_metadata = ContractTokenMetadata.from_url(token_metadata_url, self.context)

        elif parsed_url.scheme == 'ipfs':
            token_metadata = ContractTokenMetadata.from_ipfs(parsed_url.netloc, self.context)

        elif parsed_url.scheme == 'tezos-storage':
            parts = parsed_url.path.split('/')
            if len(parts) == 1:
                storage = self.storage
            elif len(parts) == 2:
                context = self._spawn_context(address=parsed_url.netloc)
                storage = ContractInterface.from_context(context).storage
            else:
                raise NotImplementedError('Unknown metadata URL scheme')
            token_metadata_json = json.loads(storage['metadata'][parts[-1]]().decode())
            token_metadata = ContractTokenMetadata.from_json(token_metadata_json, self.context)

        elif parsed_url.scheme == 'sha256':
            raise NotImplementedError

        else:
            raise NotImplementedError('Unknown metadata URL scheme')

        return token_metadata

    def _get_token_metadata_from_view(self, token_id: int) -> Optional[ContractTokenMetadata]:
        self._logger.info('Trying to fetch token %s metadata from off-chain view', token_id)
        try:
            token_metadata_json = cast(ContractMetadata, self.metadata).tokenMetadata(token_id).storage_view()[1]
            return ContractTokenMetadata.from_json(token_metadata_json)
        except KeyError:
            self._logger.info('There\'s no off-chain view named `token_metadata`')
            return None
        except MichelsonRuntimeError:
            self._logger.info('Off-chain view has no token metadata for token_id %s', token_id)
            return None

    @cached_property
    def metadata_url(self) -> Optional[str]:
        try:
            metadata = self.storage.data.find(lambda x: x.field_name == 'metadata' and isinstance(x, BigMapType))
            if metadata is not None:
                metadata_url = metadata['']
                if isinstance(metadata_url, BytesType):
                    return metadata_url.value.decode()
                else:
                    self._logger.info('Empty string key is not found in metadata big map')
            else:
                self._logger.info('Metadata big map not found')
        # FIXME: Dirty
        except (KeyError, AssertionError):
            self._logger.info('Failed to get metadata URI')
        return None

    @property
    def parameter(self) -> ContractEntrypoint:
        return self.entrypoint[self.program.parameter.root_name]

    @property  # type: ignore
    @deprecated(deprecated_in='3.0.0', removed_in='4.0.0', details='access `ContractInterface` directly')
    def contract(self) -> 'ContractInterface':
        return self

    @property  # type: ignore
    @deprecated(deprecated_in='3.0.0', removed_in='4.0.0', details='use `to_michelson()` instead')
    def text(self) -> str:
        return self.to_michelson()

    @property  # type: ignore
    @deprecated(deprecated_in='3.0.0', removed_in='4.0.0', details='use `to_micheline()` instead')
    def code(self):
        return self.to_micheline()

    @property  # type: ignore
    @deprecated(deprecated_in='3.0.0', removed_in='4.0.0', details='use `default()` instead')
    def call(self) -> ContractEntrypoint:
        return self.parameter

    def operation_result(self, operation_group: Dict[str, Any]) -> List[ContractCallResult]:
        """Get operation parameters, and resulting storage as Python objects.
        Can locate operation inside operation groups with multiple contents and/or internal operations.

        :param operation_group: {'branch', 'protocol', 'contents', 'signature'}
        :rtype: ContractCallResult
        """
        return ContractCallResult.from_run_operation(operation_group, context=self.context)

    def script(self, initial_storage=None, mode: Optional[str] = None) -> Dict[str, Any]:
        """Generate script for contract origination.

        :param initial_storage: Python object, leave None to generate default (attach shell/key for smart fill)
        :param mode: whether to use `readable` or `optimized` (or `legacy_optimized`) encoding for initial storage
        :return: {"code": $Micheline, "storage": $Micheline}
        """
        if initial_storage:
            storage = self.program.storage.from_python_object(initial_storage)
        else:
            storage = self.program.storage.dummy(self.context)
        return {
            'code': self.program.as_micheline_expr(),
            'storage': storage.to_micheline_value(mode=mode or self.context.mode, lazy_diff=True),
        }

    def originate(
        self,
        initial_storage=None,
        mode: Optional[str] = None,
        balance: Union[int, Decimal] = 0,
        delegate: Optional[str] = None,
    ) -> OperationGroup:
        """Create an origination operation

        :param initial_storage: Python object, leave None to generate default
        :param mode: whether to use `readable` or `optimized` (or `legacy_optimized`) encoding for initial storage
        :param balance: initial balance
        :param delegate: initial delegator
        :rtype: OperationGroup
        """
        return OperationGroup(context=self._spawn_context()).origination(
            script=self.script(initial_storage, mode=mode),
            balance=balance,
            delegate=delegate,
        )


@deprecated(deprecated_in='3.0.0', removed_in='4.0.0', details='use `ContractInterface` instead')
class Contract(ContractInterface):
    pass
