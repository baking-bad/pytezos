from datetime import datetime
from typing import Any
from typing import List
from typing import Optional
from typing import Tuple

from pytezos.context.abstract import AbstractContext
from pytezos.context.abstract import get_originated_address
from pytezos.crypto.encoding import base58_encode
from pytezos.crypto.key import Key
from pytezos.logging import logger
from pytezos.michelson.forge import forge_micheline
from pytezos.michelson.forge import forge_script_expr
from pytezos.michelson.micheline import get_script_section
from pytezos.michelson.micheline import get_script_sections
from pytezos.operation import DEFAULT_OPERATIONS_TTL
from pytezos.operation import MAX_OPERATIONS_TTL
from pytezos.rpc.errors import RpcError
from pytezos.rpc.shell import ShellQuery

DEFAULT_IPFS_GATEWAY = 'https://ipfs.io/ipfs'


class ExecutionContext(AbstractContext):
    def __init__(
        self,
        amount=None,
        chain_id=None,
        protocol=None,
        source=None,
        sender=None,
        balance=None,
        block_id=None,
        now=None,
        level=None,
        voting_power=None,
        total_voting_power=None,
        min_block_time=None,
        key=None,
        shell=None,
        address=None,
        counter=None,
        script=None,
        tzt=False,
        mode=None,
        ipfs_gateway=None,
        global_constants=None,
        view_results=None,
    ):
        self.key: Optional[Key] = key
        self.shell: Optional[ShellQuery] = shell
        self.counter = counter
        self.mode = mode or 'readable'
        self.block_id = block_id or 'head'
        self.address = address
        self.balance = balance
        self.amount = amount
        self.now = now
        self.level = level
        self.sender = sender
        self.source = source
        self.chain_id = chain_id
        self.protocol = protocol
        self.voting_power = voting_power
        self.total_voting_power = total_voting_power
        self.min_block_time = min_block_time
        self.tzt = tzt
        self.parameter_expr = get_script_section(script, name='parameter') if script and not tzt else None
        self.storage_expr = get_script_section(script, name='storage') if script and not tzt else None
        self.code_expr = get_script_section(script, name='code') if script else None
        self.views_expr = get_script_sections(script, name='view') if script else []
        self.input_expr = get_script_section(script, name='input') if script and tzt else None
        self.output_expr = get_script_section(script, name='output') if script and tzt else None
        self.sender_expr = get_script_section(script, name='sender') if script and tzt else None
        self.balance_expr = get_script_section(script, name='balance') if script and tzt else None
        self.amount_expr = get_script_section(script, name='amount') if script and tzt else None
        self.self_expr = get_script_section(script, name='self') if script and tzt else None
        self.now_expr = get_script_section(script, name='now') if script and tzt else None
        self.source_expr = get_script_section(script, name='source') if script and tzt else None
        self.chain_id_expr = get_script_section(script, name='chain_id') if script and tzt else None
        self.big_maps_expr = get_script_section(script, name='big_maps') if script and tzt else None
        self.origination_index = 1
        self.tmp_big_map_index = 0
        self.tmp_sapling_index = 0
        self.alloc_big_map_index = 0
        self.alloc_sapling_index = 0
        self.balance_update = 0
        self.big_maps = {}
        self.tzt_big_maps = {}
        self.view_results = view_results or {}
        self.global_constants = global_constants or {}
        self.debug = False
        self._sandboxed: Optional[bool] = None
        self.ipfs_gateway = (ipfs_gateway or DEFAULT_IPFS_GATEWAY).rstrip('/')
        self.storage_value = script.get('storage') if script else None

    def __copy__(self):
        raise ValueError("It's not allowed to copy context")

    @property
    def script(self) -> Optional[dict]:
        if self.parameter_expr and self.storage_expr and self.code_expr:
            return {
                'code': [
                    self.parameter_expr,
                    self.storage_expr,
                    self.code_expr,
                    *self.views_expr,
                ],
                'storage': self.storage_value,
            }
        else:
            return None

    @property
    def sandboxed(self) -> bool:
        if self.shell is None:
            raise Exception('`shell` is not set')
        if self._sandboxed is None:
            version = self.shell.version()
            self._sandboxed = 'SANDBOXED' in version['network_version']['chain_name']
        return self._sandboxed

    def reset(self):
        self.counter = None
        self.origination_index = 1
        self.tmp_big_map_index = 0
        self.tmp_sapling_index = 0
        self.alloc_big_map_index = 0
        self.alloc_sapling_index = 0
        self.balance_update = 0
        self.big_maps.clear()
        self.tzt_big_maps.clear()
        self.global_constants.clear()

    def set_counter(self, counter: int):
        self.counter = counter

    def get_counter(self) -> int:
        if self.counter is None:
            if not self.key:
                raise Exception('key is undefined')
            if not self.shell:
                raise Exception('shell is undefined')

            key_hash = self.key.public_key_hash()
            self.counter = int(self.shell.contracts[key_hash]()['counter'])

        self.counter += 1
        return self.counter

    def get_counter_offset(self) -> int:
        """Return current count of pending operations from the current key in mempool.
        Zero when the node has no mempool or does not expose it.
        Informational only: `autofill` does not apply it to the counter, since the mempool admits
        one manager operation per source per block (use `bulk()` to send several).
        """
        if self.key is None:
            raise Exception('`key` is not set')
        if self.shell is None:
            raise Exception('`shell` is not set')

        pending = self.shell.mempool.pending_operations.from_source(self.key.public_key_hash())
        for content in pending:
            logger.debug("pending operation in mempool: %s", content)

        logger.debug("counter offset: %s", len(pending))
        return len(pending)

    def register_big_map(self, ptr: int, copy=False) -> int:
        if copy:
            tmp_ptr = self.get_tmp_big_map_id()
            self.big_maps[tmp_ptr] = (ptr, True)
            return tmp_ptr
        else:
            self.big_maps[ptr] = (ptr, False)
            return ptr

    def get_tmp_big_map_id(self) -> int:
        self.tmp_big_map_index += 1
        return -self.tmp_big_map_index

    def get_big_map_diff(self, ptr: int) -> Tuple[Optional[int], int, str]:
        if ptr in self.big_maps:
            src_big_map, copy = self.big_maps[ptr]
            if copy:
                dst_big_map = self.alloc_big_map_index
                self.alloc_big_map_index += 1
                return src_big_map, dst_big_map, 'copy'
            else:
                return src_big_map, src_big_map, 'update'
        else:
            big_map = self.alloc_big_map_index
            self.alloc_big_map_index += 1
            return None, big_map, 'alloc'

    def get_originated_address(self) -> str:
        res = get_originated_address(self.origination_index)
        self.origination_index += 1
        return res

    def spend_balance(self, amount: int):
        balance = self.get_balance()
        assert amount <= balance, f'cannot spend {amount} tez, {balance} tez left'
        self.balance_update -= amount

    def get_parameter_expr(self, address=None) -> Optional[dict]:
        if self.shell and address:
            if address == get_originated_address(0):
                return None  # dummy callback
            else:
                script = self.shell.contracts[address].script()
                expr = get_script_section(script, name='parameter', cls=None, required=True)  # type: ignore
        elif address:
            return None
        else:
            expr = self.parameter_expr
        return self.resolve_global_constants(expr)

    def get_storage_expr(self, address=None) -> Optional[dict]:
        if self.shell and address:
            script = self.shell.contracts[address].script()
            expr = get_script_section(script, name='storage', cls=None, required=True)  # type: ignore
        elif address:
            return None
        else:
            expr = self.storage_expr
        return self.resolve_global_constants(expr)

    def get_storage_value(self, address=None) -> Optional[dict]:
        if self.shell:
            return self.shell.head.context.contracts[address].storage()
        return None if address else self.resolve_global_constants(self.storage_value)

    def get_code_expr(self):
        return self.resolve_global_constants(self.code_expr)

    def get_view_result(self, name, address=None) -> Optional[Any]:
        key = name if address is None else f'{address}%{name}'
        return self.view_results.get(key)

    def get_views_expr(self) -> List[dict]:
        return self.resolve_global_constants(self.views_expr)

    def get_view_expr(self, name, address=None) -> Optional[dict]:
        if address:
            if self.shell:
                script = self.shell.contracts[address].script()
                views = get_script_sections(script, name='view', cls=None)
            else:
                return None
        else:
            views = self.views_expr

        try:
            expr = next(view for view in views if view['args'][0]['string'] == name)
            return self.resolve_global_constants(expr)
        except (StopIteration, KeyError, IndexError):
            return None

    def get_input_expr(self):
        return self.input_expr

    def get_output_expr(self):
        return self.output_expr

    def get_sender_expr(self):
        return self.sender_expr

    def get_balance_expr(self):
        return self.balance_expr

    def get_amount_expr(self):
        return self.amount_expr

    def get_self_expr(self):
        return self.self_expr

    def get_now_expr(self):
        return self.now_expr

    def get_source_expr(self):
        return self.source_expr

    def get_chain_id_expr(self):
        return self.chain_id_expr

    def get_big_maps_expr(self):
        return self.big_maps_expr

    def set_storage_expr(self, expr):
        self.storage_expr = expr

    def set_parameter_expr(self, expr):
        self.parameter_expr = expr

    def set_code_expr(self, expr):
        self.code_expr = expr

    def set_input_expr(self, expr):
        self.input_expr = expr

    def set_output_expr(self, expr):
        self.output_expr = expr

    def set_source_expr(self, expr):
        self.source_expr = expr

    def set_chain_id_expr(self, expr):
        self.chain_id_expr = expr

    def set_big_maps_expr(self, expr):
        self.big_maps_expr = expr

    def get_big_map_value(self, ptr: int, key_hash: str):
        if self.tzt or (ptr not in self.big_maps):
            return None
        ptr, _ = self.big_maps[ptr]
        if ptr < 0:
            return None
        if self.shell is None:
            raise ValueError(f'Shell is undefined, cannot connect to network')
        try:
            return self.shell.blocks[self.block_id].context.big_maps[ptr][key_hash]()
        except RpcError:
            return None  # TODO: special exception/value | Key does not exist

    def register_sapling_state(self, ptr: int):
        raise NotImplementedError

    def get_tmp_sapling_state_id(self) -> int:
        self.tmp_sapling_index += 1
        return -self.tmp_sapling_index

    def get_sapling_state_diff(self, offset_commitment=0, offset_nullifier=0) -> Tuple[int, list]:
        ptr = self.alloc_sapling_index
        self.alloc_sapling_index += 1
        return ptr, []

    def get_self_address(self) -> str:
        return self.address or get_originated_address(0)

    def get_amount(self) -> int:
        return self.amount or 0

    def get_sender(self) -> str:
        return self.sender or self.get_dummy_key_hash()

    def get_source(self) -> str:
        return self.source or self.get_dummy_key_hash()

    def get_now(self) -> int:
        if self.now is not None:
            return self.now
        elif self.shell:
            ts = self.shell.head.header()['timestamp']
            dt = datetime.strptime(ts, '%Y-%m-%dT%H:%M:%SZ')
            first_delay = self.shell.head.context.constants().get('minimal_block_delay', 0)
            return int((dt - datetime(1970, 1, 1)).total_seconds()) + int(first_delay)
        else:
            return 0

    def get_level(self) -> int:
        if self.level is not None:
            return self.level
        elif self.shell:
            header = self.shell.blocks[self.block_id].header()
            return int(header['level'])
        else:
            return 1

    def get_balance(self) -> int:
        if self.balance is not None:
            balance = self.balance
        elif self.shell:
            contract = self.shell.contracts[self.get_self_address()]()
            balance = int(contract['balance'])
        else:
            balance = 0
        return balance + self.balance_update

    def get_voting_power(self, address: str) -> int:
        if self.voting_power is not None:
            return self.voting_power.get(address, 0)
        elif self.shell:
            raise NotImplementedError
        else:
            return 0

    def get_total_voting_power(self) -> int:
        if self.total_voting_power is not None:
            return self.total_voting_power
        elif self.shell:
            raise NotImplementedError
        else:
            return 0

    def get_min_block_time(self) -> int:
        if self.min_block_time:
            return self.min_block_time
        elif self.shell:
            constants = self.shell.head.context.constants()
            return int(constants['minimal_block_delay'])
        else:
            return 1

    def get_chain_id(self) -> str:
        if self.chain_id:
            return self.chain_id
        elif self.shell:
            return self.shell.chains.main.chain_id()
        else:
            return self.get_dummy_chain_id()

    def get_protocol(self) -> str:
        if self.protocol:
            return self.protocol
        elif self.shell:
            return self.shell.head.header()['protocol']
        else:
            raise NotImplementedError

    def get_dummy_address(self) -> str:
        if self.key:
            return self.key.public_key_hash()
        else:
            return base58_encode(b'\x00' * 20, b'KT1').decode()

    def get_dummy_txr_address(self) -> str:
        if self.key:
            return self.key.public_key_hash()
        else:
            return base58_encode(b'\x00' * 20, b'txr1').decode()

    def get_dummy_public_key(self) -> str:
        if self.key:
            return self.key.public_key()
        else:
            return base58_encode(b'\x00' * 32, b'edpk').decode()

    def get_dummy_key_hash(self) -> str:
        if self.key:
            return self.key.public_key_hash()
        else:
            return base58_encode(b'\x00' * 20, b'tz1').decode()

    def get_dummy_signature(self) -> str:
        return base58_encode(b'\x00' * 64, b'sig').decode()

    def get_dummy_chain_id(self) -> str:
        return base58_encode(b'\x00' * 4, b'Net').decode()

    def get_dummy_lambda(self):
        return {'prim': 'FAILWITH'}

    def set_total_voting_power(self, total_voting_power: int):
        self.total_voting_power = total_voting_power

    def set_voting_power(self, address: str, voting_power: int):
        self.voting_power[address] = voting_power

    def get_operations_ttl(self) -> int:
        if self.sandboxed:
            return MAX_OPERATIONS_TTL
        return DEFAULT_OPERATIONS_TTL

    def register_global_constant(self, expression):
        """Register global constant
        :param expression: Micheline expression
        """
        constant_hash = forge_script_expr(forge_micheline(expression))
        self.global_constants[constant_hash] = expression

    def resolve_global_constants(self, expression):
        """Replace global constants with their respectful values or throw an error if the constant is not defined
        :param expression: Micheline expression
        """

        def _resolve_constant(node):
            try:
                constant_hash = node['args'][0]['string']
            except (KeyError, IndexError) as e:
                raise ValueError('Unexpected constant expression') from e
            if constant_hash not in self.global_constants:
                raise KeyError(f'Constant {constant_hash} is not defined')
            return _resolve(self.global_constants[constant_hash])
            # TODO: check if global constants are really recursive

        def _resolve(node):
            if isinstance(node, dict):
                if node.get('prim') == 'constant':
                    return _resolve_constant(node)
                elif node.get('args'):
                    args = list(map(_resolve, node['args']))
                    return {k: v if k != 'args' else args for k, v in node.items()}
                else:
                    return node
            elif isinstance(node, list):
                return list(map(_resolve, node))
            else:
                return node

        return _resolve(expression)
