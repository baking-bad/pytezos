from contextlib import suppress
from typing import Any
from typing import Dict
from typing import List
from typing import Tuple
from typing import Union

import base58
import strict_rfc3339  # type: ignore

from pytezos.crypto.encoding import base58_decode
from pytezos.crypto.encoding import base58_encode
from pytezos.crypto.key import blake2b_32
from pytezos.michelson.tags import prim_tags

prim_int = {v[0]: k for k, v in prim_tags.items()}


def get_tag(args_len: int, annots_len: int) -> bytes:
    tag = min(args_len * 2 + 3 + (1 if annots_len > 0 else 0), 9)
    return bytes([tag])


def read_tag(tag: int) -> Tuple[int, bool]:
    return (tag - 3) // 2, bool((tag - 3) % 2)


def forge_int(value: int) -> bytes:
    """
    Encode signed unbounded integer into the byte form.

    :param value: signed unbounded integer
    """
    res = bytearray()
    i = abs(value)

    res.append((i & 0b00111111) | (0b11000000 if value < 0 else 0b10000000))
    i >>= 6

    while i != 0:
        res.append((i & 0b01111111) | 0b10000000)
        i >>= 7

    res[-1] &= 0b01111111
    return bytes(res)


def forge_int16(value: int) -> bytes:
    return value.to_bytes(2, 'big')


def forge_int32(value: int) -> bytes:
    return value.to_bytes(4, 'big')


def unforge_int(data: bytes) -> (int, int):  # type: ignore
    """Decode signed unbounded integer from bytes.

    :param data: Encoded integer
    :returns: tuple(parsed integer, length in bytes)
    """
    value = 0
    length = 1

    while data[length - 1] & 0b10000000 != 0:
        length += 1

    for i in range(length - 1, 0, -1):
        value <<= 7
        value |= data[i] & 0b01111111

    value <<= 6
    value |= data[0] & 0b00111111

    if (data[0] & 0b01000000) != 0:
        value = -value

    return value, length


def forge_nat(value: int) -> bytes:
    """Encode a number using LEB128 encoding (Zarith).

    :param int value: the value to encode
    :returns: encoded value
    :rtype: bytes
    """
    if value < 0:
        raise ValueError('Value cannot be negative.')

    buf = bytearray()
    more = True

    while more:
        byte = value & 0x7F
        value >>= 7

        if value:
            byte |= 0x80
        else:
            more = False

        buf.append(byte)

    return bytes(buf)


def unforge_chain_id(data: bytes) -> str:
    """Decode chain id from byte form.

    :param data: encoded chain id.
    :returns: base58 encoded chain id
    """
    return base58_encode(data, b'Net').decode()


def unforge_signature(data: bytes) -> str:
    """Decode signature from byte form.

    :param data: encoded signature.
    :returns: base58 encoded signature (generic)
    """
    return base58_encode(data, b'sig').decode()


def forge_bool(value: bool) -> bytes:
    """Encode boolean value into bytes."""
    return b'\xff' if value else b'\x00'


def forge_base58(value: str) -> bytes:
    """Encode base58 string into bytes.

    :param value: base58 encoded value (with checksum)
    """
    return base58_decode(value.encode())


def optimize_timestamp(value: str) -> int:
    """Convert time string to timestamp.

    :param value: RFC3339 time string or timestamp
    """
    assert isinstance(value, str)
    with suppress(strict_rfc3339.InvalidRFC3339Error):
        return int(strict_rfc3339.rfc3339_to_timestamp(value))
    return int(value)


def forge_address(value: str, tz_only=False) -> bytes:
    """Encode address or key hash into bytes.

    :param value: base58 encoded address or key_hash
    :param tz_only: True indicates that it's a key_hash (will be encoded in a more compact form)
    """
    prefix_len = 4 if value.startswith('txr1') else 3
    prefix = value[:prefix_len]
    address = base58.b58decode_check(value)[prefix_len:]

    if prefix == 'tz1':
        res = b'\x00\x00' + address
    elif prefix == 'tz2':
        res = b'\x00\x01' + address
    elif prefix == 'tz3':
        res = b'\x00\x02' + address
    elif prefix == 'tz4':
        res = b'\x00\x03' + address
    elif prefix == 'KT1':
        res = b'\x01' + address + b'\x00'
    elif prefix == 'txr1':
        res = b'\x02' + address + b'\x00'
    elif prefix == 'sr1':
        res = b'\x03' + address + b'\x00'
    else:
        raise ValueError(f'Can\'t forge address: unknown prefix `{prefix}`')

    return res[1:] if tz_only else res


def unforge_address(data: bytes) -> str:
    """Decode address or key_hash from bytes.

    :param data: encoded address or key_hash
    :returns: base58 encoded address
    """
    tz_prefixes = {
        b'\x00\x00': b'tz1',
        b'\x00\x01': b'tz2',
        b'\x00\x02': b'tz3',
        b'\x00\x03': b'tz4',
    }

    for bin_prefix, tz_prefix in tz_prefixes.items():
        if data.startswith(bin_prefix):
            return base58_encode(data[2:], tz_prefix).decode()

    if data.startswith(b'\x01') and data.endswith(b'\x00'):
        return base58_encode(data[1:-1], b'KT1').decode()
    elif data.startswith(b'\x02') and data.endswith(b'\x00'):
        return base58_encode(data[1:-1], b'txr1').decode()
    elif data.startswith(b'\x03') and data.endswith(b'\x00'):
        return base58_encode(data[1:-1], b'sr1').decode()
    else:
        return base58_encode(data[1:], tz_prefixes[b'\x00' + data[:1]]).decode()


def forge_contract(value: str) -> bytes:
    """Encode a value of contract type (address + optional entrypoint) into bytes.

    :param value: 'tz12345' or 'tz12345%default'
    """
    parts = value.split('%')
    address, entrypoint = (parts[0], parts[1]) if len(parts) == 2 else (parts[0], 'default')
    res = forge_address(address)
    if entrypoint != 'default':
        res += entrypoint.encode()
    return res


def unforge_contract(data: bytes) -> str:
    """Decode contract (address + optional entrypoint) from bytes

    :param data: encoded contract
    :returns: base58 encoded address and entrypoint (if exists) separated by `%`
    """
    res = unforge_address(data[:22])
    if len(data) > 22:
        res += f'%{data[22:].decode()}'
    return res


def forge_public_key(value: str) -> bytes:
    """Encode public key into bytes.

    :param value: public key in base58 form
    """
    prefix = value[:4]
    res = base58.b58decode_check(value)[4:]

    if prefix == 'edpk':  # noqa: SIM116
        return b'\x00' + res
    elif prefix == 'sppk':
        return b'\x01' + res
    elif prefix == 'p2pk':
        return b'\x02' + res
    elif prefix == 'BLpk':
        return b'\x03' + res

    raise ValueError(f'Unrecognized key type: #{prefix}')


def unforge_public_key(data: bytes) -> str:
    """Decode public key from byte form.

    :param data: encoded public key.
    :returns: base58 encoded public key
    """
    key_prefix = {
        b'\x00': b'edpk',
        b'\x01': b'sppk',
        b'\x02': b'p2pk',
        b'\x03': b'BLpk',
    }
    return base58_encode(data[1:], key_prefix[data[:1]]).decode()


def forge_array(data: bytes, len_bytes=4) -> bytes:
    """Encode array of bytes (prepend length).

    :param data: list of bytes
    :param len_bytes: number of bytes to store array length
    """
    return len(data).to_bytes(len_bytes, 'big') + data


def unforge_array(data: bytes, len_bytes=4) -> tuple:
    """Decode array of bytes.

    :param data: encoded array
    :param len_bytes: number of bytes to store array length
    :returns: Tuple[list of bytes, array length]
    """
    assert len(data) >= len_bytes, f'not enough bytes to parse array length, wanted {len_bytes}'
    length = int.from_bytes(data[:len_bytes], 'big')
    assert len(data) >= len_bytes + length, f'not enough bytes to parse array body, wanted {length}'
    return data[len_bytes : len_bytes + length], len_bytes + length


def forge_micheline(data: Union[List, Dict]) -> bytes:
    """Encode a Micheline expression into the byte form.

    :param data: Micheline expression
    """
    res = []

    if isinstance(data, list):
        res.append(b'\x02')
        res.append(forge_array(b''.join(map(forge_micheline, data))))

    elif isinstance(data, dict):
        if data.get('prim'):
            args_len = len(data.get('args', []))
            annots_len = len(data.get('annots', []))

            res.append(get_tag(args_len, annots_len))
            res.append(prim_tags[data['prim']])

            if args_len > 0:
                args = b''.join(map(forge_micheline, data['args']))
                if args_len < 3:
                    res.append(args)
                else:
                    res.append(forge_array(args))

            if annots_len > 0:
                res.append(forge_array(' '.join(data['annots']).encode()))
            elif args_len >= 3:
                res.append(b'\x00' * 4)

        elif data.get('bytes') is not None:
            res.append(b'\x0a')
            res.append(forge_array(bytes.fromhex(data['bytes'])))

        elif data.get('int') is not None:
            res.append(b'\x00')
            res.append(forge_int(int(data['int'])))

        elif data.get('string') is not None:
            res.append(b'\x01')
            res.append(forge_array(data['string'].encode()))
        else:
            raise AssertionError(data)
    else:
        raise AssertionError(data)

    return b''.join(res)


def unforge_micheline(data: bytes) -> Union[List, Dict]:
    """Parse Micheline JSON from bytes.

    :param data: Forged Micheline expression
    :returns: Micheline JSON
    """
    ptr = 0

    def unforge_sequence():
        nonlocal ptr
        _, offset = unforge_array(data[ptr:])
        end, res = ptr + offset, []
        ptr += 4
        while ptr < end:
            res.append(unforge())
        assert ptr == end, f'out of sequence boundaries'
        return res

    def unforge_prim_expr(args_len=0, annots=False):
        nonlocal ptr
        prim_tag = data[ptr]
        ptr += 1
        expr = {'prim': prim_int[prim_tag]}

        if 0 < args_len < 3:
            expr['args'] = [unforge() for _ in range(args_len)]
        elif args_len == 3:
            expr['args'] = unforge_sequence()
        else:
            assert args_len == 0, f'unexpected args len {args_len}'

        if annots or args_len == 3:
            value, offset = unforge_array(data[ptr:])
            ptr += offset
            if len(value) > 0:
                expr['annots'] = value.decode().split(' ')

        return expr

    def unforge():
        nonlocal ptr
        tag = data[ptr]
        ptr += 1
        if tag == 0:
            value, offset = unforge_int(data[ptr:])
            ptr += offset
            return {'int': str(value)}
        elif tag == 1:
            value, offset = unforge_array(data[ptr:])
            ptr += offset
            return {'string': value.decode()}
        elif tag == 2:
            return unforge_sequence()
        elif 2 < tag < 10:
            args_len, annots = read_tag(tag)
            return unforge_prim_expr(args_len, annots)
        elif tag == 10:
            value, offset = unforge_array(data[ptr:])
            ptr += offset
            return {'bytes': value.hex()}
        else:
            raise AssertionError(f'unkonwn tag {tag} at position {ptr}')

    result = unforge()
    assert ptr == len(data), f'have not reach EOS (pos {ptr}/{len(data)})'
    return result


def forge_script(script: Dict[str, Any]) -> bytes:
    """Encode an origination script into the byte form.

    :param script: {"code": "$Micheline_expression", "storage": "$Micheline_expression"}
    """
    code = forge_micheline(script['code'])
    storage = forge_micheline(script['storage'])
    return forge_array(code) + forge_array(storage)


def forge_script_expr(packed_key: bytes) -> str:
    data = blake2b_32(packed_key).digest()
    return base58_encode(data, b'expr').decode()
