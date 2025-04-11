from typing import Any
from typing import Dict
from typing import List

from pytezos.michelson.forge import forge_array
from pytezos.michelson.forge import forge_base58
from pytezos.michelson.forge import optimize_timestamp


def bump_fitness(fitness: List[str]) -> List[str]:
    if len(fitness) == 0:
        version = 2
        level = 1
        tail = ['', 'ffffffff', '00000000']
    else:
        version = int.from_bytes(bytes.fromhex(fitness[0]), 'big')
        level = int.from_bytes(bytes.fromhex(fitness[1]), 'big') + 1
        tail = ['', 'ffffffff', '00000000']  # locked_round, neg_predecessor_round, round
    return [version.to_bytes(1, 'big').hex(), level.to_bytes(4, 'big').hex(), *tail]


def forge_int_fixed(value: int, length: int) -> bytes:
    return value.to_bytes(length, 'big')


def forge_command(command: str) -> bytes:
    if command == 'activate':
        return b'\x00'
    raise NotImplementedError(command)


def forge_fitness(fitness: List[str]) -> bytes:
    return forge_array(b''.join(map(lambda x: forge_array(bytes.fromhex(x)), fitness)))


def forge_content(content: Dict[str, Any]) -> bytes:
    res = b''
    res += forge_command(content['command'])
    res += forge_base58(content['hash'])
    res += forge_fitness(content['fitness'])
    res += bytes.fromhex(content['protocol_parameters'])
    return res


def forge_protocol_data(protocol_data: Dict[str, Any]) -> bytes:
    res = b''
    if protocol_data.get('content'):
        res += forge_content(protocol_data['content'])
    else:
        res += forge_base58(protocol_data['payload_hash'])
        res += forge_int_fixed(protocol_data['payload_round'], 4)
        res += bytes.fromhex(protocol_data['proof_of_work_nonce'])
        if protocol_data.get('seed_nonce_hash'):
            res += b'\xff'
            res += forge_base58(protocol_data['seed_nonce_hash'])
        else:
            res += b'\x00'
        if protocol_data.get('liquidity_baking_toggle_vote'):
            res += b'\x01' if protocol_data['liquidity_baking_toggle_vote'] else b'\x00'
        else:
            res += b'\xff' if protocol_data['liquidity_baking_escape_vote'] else b'\x00'

    return res


def forge_block_header(shell_header: Dict[str, Any]) -> bytes:
    res = forge_int_fixed(shell_header['level'], 4)
    res += forge_int_fixed(shell_header['proto'], 1)
    res += forge_base58(shell_header['predecessor'])
    res += forge_int_fixed(optimize_timestamp(shell_header['timestamp']), 8)
    res += forge_int_fixed(shell_header['validation_pass'], 1)
    res += forge_base58(shell_header['operations_hash'])
    res += forge_fitness(shell_header['fitness'])
    res += forge_base58(shell_header['context'])
    res += bytes.fromhex(shell_header['protocol_data'])
    return res
