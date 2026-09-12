from enum import Enum
from typing import Any
from typing import Dict
from typing import List

from pytezos.michelson.forge import forge_array
from pytezos.michelson.forge import forge_base58
from pytezos.michelson.forge import optimize_timestamp


class PerBlockVote(str, Enum):
    """Per-block vote value (liquidity baking, adaptive issuance)"""

    ON = 'on'
    OFF = 'off'
    PASS = 'pass'

    def __str__(self) -> str:
        return self.value

    @property
    def tag(self) -> int:
        """Two-bit case tag of the vote in the compact `per_block_votes` encoding"""
        return per_block_vote_tags[self]


per_block_vote_tags = {
    PerBlockVote.ON: 0,
    PerBlockVote.OFF: 1,
    PerBlockVote.PASS: 2,
}


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


def forge_per_block_votes(protocol_data: Dict[str, Any]) -> bytes:
    """Forge the per-block votes byte of a block header.

    Ithaca headers carry a boolean ``liquidity_baking_escape_vote``; later protocols carry
    ``liquidity_baking_toggle_vote`` (on/off/pass) and, in Oxford..Seoul only, ``adaptive_issuance_vote``
    packed into the same byte.

    :param protocol_data: block header protocol data (JSON)
    :raises ValueError: on a vote value other than on/off/pass
    """
    if 'liquidity_baking_toggle_vote' not in protocol_data:
        return b'\xff' if protocol_data['liquidity_baking_escape_vote'] else b'\x00'
    tag = PerBlockVote(protocol_data['liquidity_baking_toggle_vote']).tag
    if protocol_data.get('adaptive_issuance_vote') is not None:
        tag |= PerBlockVote(protocol_data['adaptive_issuance_vote']).tag << 2
    return forge_int_fixed(tag, 1)


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
        res += forge_per_block_votes(protocol_data)

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
