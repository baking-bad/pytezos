from pprint import pformat
from typing import Any
from typing import Dict
from typing import List
from typing import Optional
from typing import Union

from deprecation import deprecated  # type: ignore

from pytezos.context.impl import ExecutionContext
from pytezos.context.mixin import ContextMixin
from pytezos.crypto.encoding import base58_decode
from pytezos.crypto.encoding import base58_encode
from pytezos.crypto.encoding import is_bh
from pytezos.crypto.key import blake2b_32
from pytezos.jupyter import get_class_docstring
from pytezos.logging import logger
from pytezos.michelson.forge import forge_base58
from pytezos.operation import DEFAULT_BURN_RESERVE
from pytezos.operation import DEFAULT_GAS_RESERVE
from pytezos.operation import MAX_OPERATIONS_TTL
from pytezos.operation.content import ContentMixin
from pytezos.operation.fees import calculate_fee
from pytezos.operation.fees import default_fee
from pytezos.operation.fees import default_gas_limit
from pytezos.operation.fees import default_storage_limit
from pytezos.operation.forge import forge_operation_group
from pytezos.operation.result import OperationResult
from pytezos.rpc.errors import RpcError
from pytezos.rpc.kind import validation_passes


class OperationGroup(ContextMixin, ContentMixin):
    """Operation group representation: contents (single or multiple), signature, other fields,
    and also useful helpers for filling with precise fees, signing, forging, and injecting.
    """

    def __init__(
        self,
        context: ExecutionContext,
        contents: Optional[List[Dict[str, Any]]] = None,
        protocol: Optional[str] = None,
        chain_id: Optional[str] = None,
        branch: Optional[str] = None,
        signature: Optional[str] = None,
        opg_hash: Optional[str] = None,
        opg_result: Optional[Dict[str, Any]] = None,
    ) -> None:
        super().__init__(context=context)
        self.contents = contents or []
        self.protocol = protocol
        self.chain_id = chain_id
        self.branch = branch
        self.signature = signature
        self.opg_hash = opg_hash
        self.opg_result = opg_result

    def __repr__(self) -> str:
        res = [
            super().__repr__(),
            '\nPayload',
            pformat(self.json_payload()),
            '\nHash',
            self.opg_hash or '(Not sent)' '\nHelpers',
            get_class_docstring(self.__class__),
        ]
        return '\n'.join(res)

    def _spawn(self, **kwargs) -> 'OperationGroup':
        return OperationGroup(
            context=self.context,
            contents=kwargs.get('contents', self.contents.copy()),
            protocol=kwargs.get('protocol', self.protocol),
            chain_id=kwargs.get('chain_id', self.chain_id),
            branch=kwargs.get('branch', self.branch),
            signature=kwargs.get('signature', self.signature),
            opg_hash=kwargs.get('opg_hash', self.opg_hash),
            opg_result=kwargs.get('opg_result', self.opg_result),
        )

    def json_payload(self) -> Dict[str, Any]:
        """Get JSON payload used for the injection."""
        return {
            'protocol': self.protocol,
            'branch': self.branch,
            'contents': self.contents,
            'signature': self.signature,
        }

    def binary_payload(self) -> bytes:
        """Get binary payload used for injection/hash calculation."""
        if not self.signature:
            raise ValueError('Not signed')

        return bytes.fromhex(self.forge()) + forge_base58(self.signature)

    def operation(self, content: Dict[str, Any]) -> 'OperationGroup':
        """Create new operation group with extra content added.

        :param content: Kind-specific operation body
        :rtype: OperationGroup
        """
        return self._spawn(contents=self.contents + [content])

    def fill(
        self,
        counter: Optional[int] = None,
        ttl: Optional[int] = None,
        gas_limit: Optional[int] = None,
        storage_limit: Optional[int] = None,
        minimal_nanotez_per_gas_unit: Optional[int] = None,
        **kwargs,
    ) -> 'OperationGroup':
        """Try to fill all fields left unfilled, use approximate fees
        (not optimal, use `autofill` to simulate operation and get precise values).

        :param counter: Override counter value (for manual handling)
        :param ttl: Number of blocks to wait in the mempool before removal (default is 5 for public network, MAX for sandbox),
            -1 for MAX (if you have a private network and issues with block RPC queries)
        :param gas_limit: Override gas_limit value (for manual handling)
        :param storage_limit: Override storage_limit value (for manual handling)
        :param minimal_nanotez_per_gas_unit: Override minimal_nanotez_per_gas_unit constant (for manual handling)
        :rtype: OperationGroup
        """
        if kwargs.get('branch_offset') is not None:
            logger.warning('`branch_offset` argument is deprecated, use `ttl` instead')
            ttl = MAX_OPERATIONS_TTL - kwargs['branch_offset']

        if ttl is None:
            ttl = self.context.get_operations_ttl()
        elif ttl == -1:
            ttl = MAX_OPERATIONS_TTL
        if not 0 < ttl <= MAX_OPERATIONS_TTL:
            raise Exception(f'`ttl` has to be in range (0, {MAX_OPERATIONS_TTL}]')

        chain_id = self.chain_id or self.context.get_chain_id()
        protocol = self.protocol or self.context.get_protocol()
        branch = self.branch or self.shell.blocks[f'head~{MAX_OPERATIONS_TTL - ttl}'].hash()
        source = self.key.public_key_hash()
        constants = self.shell.head.context.constants()

        if counter is not None:
            self.context.set_counter(counter - 1)  # which is supposedly the current state (head)

        if gas_limit is None:
            hard_gas_limit_per_content = int(constants['hard_gas_limit_per_operation']) // len(self.contents)
        else:
            hard_gas_limit_per_content = gas_limit // len(self.contents)

        if storage_limit is None:
            hard_storage_limit_per_content = int(constants['hard_storage_limit_per_operation']) // len(self.contents)
        else:
            hard_storage_limit_per_content = storage_limit // len(self.contents)

        replace_map = {
            'pkh': source,
            'source': source,
            'delegate': source,  # self registration
            'counter': lambda i, x: str(self.context.get_counter()),
            'secret': lambda i, x: self.key.activation_code,
            'period': lambda i, x: str(self.shell.head.voting_period()),
            'public_key': lambda i, x: self.key.public_key(),
            'gas_limit': lambda i, x: str(
                min(
                    hard_gas_limit_per_content,
                    gas_limit if gas_limit is not None else default_gas_limit(x, constants),
                )
            ),
            'storage_limit': lambda i, x: str(
                min(
                    hard_storage_limit_per_content,
                    storage_limit if storage_limit is not None else default_storage_limit(x, constants),
                )
            ),
            'fee': lambda i, x: str(default_fee(x, gas_limit, minimal_nanotez_per_gas_unit) if i == 0 else 0),
        }

        def fill_content(idx, content):
            content = content.copy()
            for k, v in replace_map.items():
                if content.get(k) in ['', '0']:
                    content[k] = v(idx, content) if callable(v) else v
            return content

        return self._spawn(
            contents=[fill_content(idx=i, content=x) for i, x in enumerate(self.contents)],
            protocol=protocol,
            chain_id=chain_id,
            branch=branch,
        )

    def run(self, block_id: str = 'head'):
        """Simulate operation without signature checks.

        :param block_id: Specify a level at which this operation should be applied (default is head)
        :returns: RPC response from `run_operation`
        """
        return self.shell.blocks[block_id].helpers.scripts.run_operation.post(
            {
                'operation': {
                    'branch': self.branch,
                    'contents': self.contents,
                    'signature': base58_encode(b'0' * 64, b'sig').decode(),
                },
                'chain_id': self.chain_id,
            }
        )

    def forge(self, validate=False) -> str:
        """Convert json representation of the operation group into bytes.

        :param validate: Forge remotely also and compare results, default is False
        :returns: Hex string
        """
        payload = {
            'branch': self.branch,
            'contents': self.contents,
        }
        local_data = forge_operation_group(payload).hex()

        if validate:
            remote_data = self.shell.blocks[self.branch].helpers.forge.operations.post(payload)
            if local_data != remote_data:
                raise ValueError(f'Local forge result differs from remote one:\n\n{local_data}\n\n{remote_data}')

        return local_data

    def message(self, block: Union[str, int] = 'genesis') -> bytes:
        """Get payload for the failing noop operation

        :param block: Specify operation branch (default is genesis)
        :returns: Message bytes
        """
        if len(self.contents) != 1 or self.contents[0]['kind'] != 'failing_noop':
            raise NotImplementedError('Use for signing messages only')

        branch = block if is_bh(str(block)) else self.shell.blocks[block].hash()
        return b'\x03' + bytes.fromhex(self._spawn(branch=branch).forge())

    def autofill(
        self,
        gas_reserve: int = DEFAULT_GAS_RESERVE,
        burn_reserve: int = DEFAULT_BURN_RESERVE,
        counter: Optional[int] = None,
        ttl: Optional[int] = None,
        fee: Optional[int] = None,
        gas_limit: Optional[int] = None,
        storage_limit: Optional[int] = None,
        **kwargs,
    ) -> 'OperationGroup':
        """Fill the gaps and then simulate the operation in order to calculate fee, gas/storage limits.

        :param gas_reserve: Add a safe reserve for dynamically calculated gas limit (default is 100).
        :param burn_reserve: Add a safe reserve for dynamically calculated storage limit (default is 100).
        :param counter: Override counter value (for manual handling)
        :param ttl: Number of blocks to wait in the mempool before removal (default is 5 for public network, 60 for sandbox)
        :param fee: Explicitly set fee for operation. If not set fee will be calculated depending on results of operation dry-run.
        :param gas_limit: Explicitly set gas limit for operation. If not set gas limit will be calculated depending on results of
            operation dry-run. In case of batch will be evenly split between operations.
        :param storage_limit: Explicitly set storage limit for operation. If not set storage limit will be calculated depending on
            results of operation dry-run. In case of batch will be evenly split between operations.
        :rtype: OperationGroup
        """
        if kwargs.get('branch_offset') is not None:
            logger.warning('`branch_offset` argument is deprecated, use `ttl` instead')
            ttl = MAX_OPERATIONS_TTL - kwargs['branch_offset']

        opg = self.fill(counter=counter, ttl=ttl)
        opg_with_metadata = opg.run()
        if not OperationResult.is_applied(opg_with_metadata):
            raise RpcError.from_errors(OperationResult.errors(opg_with_metadata))

        fee_acc = 0
        extra_size = 32 + 64  # size of serialized branch and signature + safe reserve
        num_contents = len(opg_with_metadata['contents'])
        opg.contents.clear()

        for content in opg_with_metadata['contents']:
            if validation_passes[content['kind']] == 3:
                if gas_limit is not None:
                    gas_limit_new = gas_limit // num_contents
                else:
                    gas_limit_new = OperationResult.consumed_gas(content)
                    if content['kind'] in ['origination', 'transaction']:
                        gas_limit_new += gas_reserve

                if storage_limit is not None:
                    storage_limit_new = storage_limit // num_contents
                else:
                    paid_storage_size_diff = OperationResult.paid_storage_size_diff(content)
                    burned = OperationResult.burned(content)
                    storage_limit_new = paid_storage_size_diff + burned
                    if content['kind'] in ['origination', 'transaction']:
                        storage_limit_new += burn_reserve

                # Counter stays as filled: the mempool admits one manager op per source per block, use `bulk()` for several
                content.update(
                    gas_limit=str(gas_limit_new),
                    storage_limit=str(storage_limit_new),
                    fee='0',
                )
                fee_acc += calculate_fee(content, gas_limit_new, extra_size=1 + extra_size // num_contents)

            content.pop('metadata')
            logger.debug("autofilled transaction content: %s" % content)
            opg.contents.append(content)

        if fee or fee_acc:
            opg.contents[0]['fee'] = str(fee if fee is not None else fee_acc)

        return opg

    def sign(self) -> 'OperationGroup':
        """Sign the operation group with the key specified by `using`.

        :rtype: OperationGroup
        """
        validation_pass = validation_passes[self.contents[0]['kind']]
        if any(map(lambda x: validation_passes[x['kind']] != validation_pass, self.contents)):
            raise ValueError('Mixed validation passes')

        if validation_pass == 0:
            if self.chain_id is None:
                raise ValueError('Chain ID is undefined, run .fill first')
            watermark = b'\x02' + base58_decode(self.chain_id.encode())
        else:
            watermark = b'\x03'

        message = watermark + bytes.fromhex(self.forge())
        signature = self.key.sign(message=message, generic=True)

        return self._spawn(signature=signature)

    def hash(self) -> str:
        """Calculate the Base58 encoded operation group hash."""
        hash_digest = blake2b_32(self.binary_payload()).digest()
        return base58_encode(hash_digest, b'o').decode()

    def run_operation(self, block_id: str = 'head'):
        """Simulate operation without signature checks.

        :param block_id: Specify a level at which this operation should be applied (default is head)
        :returns: RPC response from `run_operation`
        """
        return self.run(block_id)

    @deprecated(deprecated_in='3.1.0', removed_in='4.0.0', details='use `run_operation()` instead')
    def preapply(self):
        """Preapply signed operation group.

        :returns: RPC response from `preapply`
        """
        if not self.signature:
            raise ValueError('Not signed')

        return self.run_operation()

    def send(
        self,
        gas_reserve: int = DEFAULT_GAS_RESERVE,
        burn_reserve: int = DEFAULT_BURN_RESERVE,
        min_confirmations: int = 0,
        ttl: Optional[int] = None,
    ) -> 'OperationGroup':
        """

        :param gas_reserve: Add a safe reserve for dynamically calculated gas limit (default is 100).
        :param burn_reserve: Add a safe reserve for dynamically calculated storage limit (default is 100).
        :param min_confirmations: number of block injections to wait for before returning (default is 0, i.e. async mode)
        :param ttl: Number of blocks to wait in the mempool before removal (default is 5 for public network, 60 for sandbox)
        :return: OperationGroup with hash filled
        """
        if ttl is None:
            ttl = self.context.get_operations_ttl()

        opg = self.autofill(gas_reserve=gas_reserve, burn_reserve=burn_reserve, ttl=ttl).sign()
        res = opg.inject(min_confirmations=min_confirmations, num_blocks_wait=ttl)
        return opg._spawn(opg_hash=res['hash'], opg_result=res)

    def send_async(
        self,
        ttl: int,
        counter: int,
        gas_limit: int,
        storage_limit: int,
        minimal_nanotez_per_gas_unit: Optional[int] = None,
    ) -> 'OperationGroup':
        """
        Send operation without simulation or pre-validation

        :param ttl: Number of blocks to wait in the mempool before removal (default is 5 for public network, 60 for sandbox)
        :param counter: Set counter value
        :param gas_limit: Set gas_limit value
        :param storage_limit: Set storage_limit value
        :param minimal_nanotez_per_gas_unit: Override minimal_nanotez_per_gas_unit constant
        :rtype: OperationGroup
        """
        opg = self.fill(
            counter=counter,
            ttl=ttl,
            gas_limit=gas_limit,
            storage_limit=storage_limit,
            minimal_nanotez_per_gas_unit=minimal_nanotez_per_gas_unit,
        ).sign()
        res = opg.inject(prevalidate=False)
        return opg._spawn(opg_hash=res['hash'])

    def inject(
        self,
        check_result: bool = True,
        num_blocks_wait: int = 5,
        time_between_blocks: Optional[int] = None,
        block_timeout: Optional[int] = None,
        min_confirmations: int = 0,
        prevalidate: bool = True,
        **kwargs,
    ):
        """Inject the signed operation group.

        :param check_result: raise RpcError in case operation is applied but has runtime errors
        :param num_blocks_wait: number of blocks to wait for injection
        :param time_between_blocks: override the corresponding parameter from constants
        :param block_timeout: set block timeout (by default Pytezos will wait for a long time)
        :param min_confirmations: number of block injections to wait for before returning
        :param prevalidate: ask node to pre-validate the operation before the injection (True by default)
        :returns: operation group with metadata (raw RPC response)
        """
        self.context.reset()  # reset counter

        opg_hash = self.shell.injection.operation.post(
            operation=self.binary_payload(),
            _async=not prevalidate,
        )

        if min_confirmations == 0:
            return {
                'chain_id': self.chain_id,
                'hash': opg_hash,
                **self.json_payload(),
            }

        operations = self.shell.wait_operations(
            opg_hashes=[opg_hash],
            ttl=num_blocks_wait,
            min_confirmations=min_confirmations,
            time_between_blocks=time_between_blocks,
            block_timeout=block_timeout,
        )

        assert len(operations) == 1
        if check_result:
            if not OperationResult.is_applied(operations[0]):
                raise RpcError.from_errors(OperationResult.errors(operations[0]))

        return operations[0]

    @deprecated(deprecated_in='3.1.0', removed_in='4.0.0', details='use `run_operation()` instead')
    def result(self) -> List[OperationResult]:
        """Parse the preapply result.

        :rtype: List[OperationResult]
        """
        return OperationResult.from_operation_group(self.preapply())
