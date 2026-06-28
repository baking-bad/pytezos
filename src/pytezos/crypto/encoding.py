from typing import Union

import base58

tb = bytes

base58_encodings = [
    #    Encoded   |               Decoded             |
    # prefix | len | prefix                      | len | Data type
    (b'B', 51, tb([1, 52]), 32, 'block hash'),
    (b'o', 51, tb([5, 116]), 32, 'operation hash'),
    (b'Lo', 52, tb([133, 233]), 32, 'operation list hash'),
    (b'LLo', 53, tb([29, 159, 109]), 32, 'operation list list hash'),
    (b'P', 51, tb([2, 170]), 32, 'protocol hash'),
    (b'Co', 52, tb([79, 199]), 32, 'context hash'),
    (b'tz1', 36, tb([6, 161, 159]), 20, 'ed25519 public key hash'),
    (b'tz2', 36, tb([6, 161, 161]), 20, 'secp256k1 public key hash'),
    (b'tz3', 36, tb([6, 161, 164]), 20, 'p256 public key hash'),
    (b'tz4', 36, tb([6, 161, 166]), 20, 'BLS12-381 (MinPk) public key hash'),
    (b'tz5', 36, tb([6, 161, 169]), 20, 'ML-DSA-44 public key hash'),
    (b'KT1', 36, tb([2, 90, 121]), 20, 'originated smart contract address'),
    (b'txr1', 37, tb([1, 128, 120, 31]), 20, 'tx_rollup_l2_address'),
    (b'sr1', 36, tb([6, 124, 117]), 20, 'originated smart rollup address'),
    (b'src1', 54, tb([17, 165, 134, 138]), 32, 'smart rollup commitment hash'),
    (b'srs1', 54, tb([17, 165, 235, 240]), 32, 'smart rollup state hash'),
    (b'srib1', 55, tb([3, 255, 138, 145, 110]), 32, 'smart rollup inbox'),
    (b'srib2', 55, tb([3, 255, 138, 145, 140]), 32, 'smart rollup merkelized payload'),
    (b'id', 30, tb([153, 103]), 16, 'cryptobox public key hash'),
    (b'expr', 54, tb([13, 44, 64, 27]), 32, 'script expression'),
    (b'edsk', 54, tb([13, 15, 58, 7]), 32, 'ed25519 seed'),
    (b'edpk', 54, tb([13, 15, 37, 217]), 32, 'ed25519 public key'),
    (b'spsk', 54, tb([17, 162, 224, 201]), 32, 'secp256k1 secret key'),
    (b'p2sk', 54, tb([16, 81, 238, 189]), 32, 'p256 secret key'),
    (b'edesk', 88, tb([7, 90, 60, 179, 41]), 56, 'ed25519 encrypted seed'),
    (b'spesk', 88, tb([9, 237, 241, 174, 150]), 56, 'secp256k1 encrypted secret key'),
    (b'p2esk', 88, tb([9, 48, 57, 115, 171]), 56, 'p256_encrypted_secret_key'),
    (b'sppk', 55, tb([3, 254, 226, 86]), 33, 'secp256k1 public key'),
    (b'p2pk', 55, tb([3, 178, 139, 127]), 33, 'p256 public key'),
    (b'SSp', 53, tb([38, 248, 136]), 33, 'secp256k1 scalar'),
    (b'GSp', 53, tb([5, 92, 0]), 33, 'secp256k1 element'),
    (b'edsk', 98, tb([43, 246, 78, 7]), 64, 'ed25519 secret key'),
    (b'edsig', 99, tb([9, 245, 205, 134, 18]), 64, 'ed25519 signature'),
    (b'spsig', 99, tb([13, 115, 101, 19, 63]), 64, 'secp256k1 signature'),
    (b'p2sig', 98, tb([54, 240, 44, 52]), 64, 'p256 signature'),
    (b'sig', 96, tb([4, 130, 43]), 64, 'generic signature'),
    (b'Net', 15, tb([87, 82, 0]), 4, 'chain id'),
    (b'nce', 53, tb([69, 220, 169]), 32, 'seed nonce hash'),
    (b'btz1', 37, tb([1, 2, 49, 223]), 20, 'blinded public key hash'),
    (b'vh', 52, tb([1, 106, 242]), 32, 'block_payload_hash'),
    (b'BLsig', 142, tb([40, 171, 64, 207]), 96, 'bls12_381_min_pk signature'),
    (b'BLpk', 76, tb([6, 149, 135, 204]), 48, 'bls12_381_min_pk public_key'),
    (b'BLsk', 54, tb([3, 150, 192, 40]), 32, 'bls12_381 secret_key'),
    (b'BLesk', 88, tb([2, 5, 30, 53, 25]), 56, 'bls12_381 encrypted_secret_key'),
    (b'mdpk', 1802, tb([13, 7, 237, 67]), 1312, 'ML-DSA-44 public key'),
    (b'mdsk', 5298, tb([9, 57, 116, 57]), 3872, 'ML-DSA-44 secret key'),
    (b'mdesk', 5332, tb([5, 49, 133, 39, 172]), 3896, 'ML-DSA-44 encrypted secret key'),
    (b'mdsig', 3316, tb([1, 156, 45, 210, 3]), 2420, 'ML-DSA-44 signature'),
]

operation_tags = {
    'endorsement': 0,
    'seed_nonce_revelation': 1,
    'double_endorsement_evidence': 2,
    'double_baking_evidence': 3,
    'account_activation': 4,
    'proposals': 5,
    'ballot': 6,
    'reveal': 7,
    'transaction': 8,
    'origination': 9,
    'delegation': 10,
}


def scrub_input(v: Union[str, bytes]) -> bytes:
    if isinstance(v, bytes):
        return v
    elif isinstance(v, str):
        try:
            return bytes.fromhex(v.removeprefix('0x'))
        except ValueError:
            return v.encode('ascii')
    else:
        raise TypeError('A bytes-like object is required (also str), not `%s`' % type(v).__name__)


def base58_decode(v: bytes) -> bytes:
    """Decode data using Base58 with checksum + validate binary prefix against known kinds and cut in the end.

    :param v: Array of bytes (use string.encode())
    :returns: bytes
    """
    try:
        prefix_len = next(
            len(encoding[2]) for encoding in base58_encodings if len(v) == encoding[1] and v.startswith(encoding[0])
        )
    except StopIteration as e:
        raise ValueError('Invalid encoding, prefix or length mismatch.') from e

    return base58.b58decode_check(v)[prefix_len:]


def base58_encode(v: bytes, prefix: bytes) -> bytes:
    """Encode data using Base58 with checksum and add an according binary prefix in the end.

    :param v: Array of bytes
    :param prefix: Human-readable prefix (use b'') e.g. b'tz', b'KT', etc
    :returns: bytes (use string.decode())
    """
    try:
        encoding = next(encoding for encoding in base58_encodings if len(v) == encoding[3] and prefix == encoding[0])
    except StopIteration as e:
        raise ValueError('Invalid encoding, prefix or length mismatch.') from e
    return base58.b58encode_check(encoding[2] + v)


def _validate(v: Union[str, bytes], prefixes: list):
    if isinstance(v, str):
        v = v.encode()
    v = scrub_input(v)
    if any(map(v.startswith, prefixes)):
        base58_decode(v)
    else:
        raise ValueError('Unknown prefix.')


def validate_pkh(v: Union[str, bytes]):
    """Ensure parameter is a public key hash (starts with b'tz1', b'tz2', b'tz3', b'tz4', b'tz5')

    :param v: string or bytes
    :raises ValueError: if parameter is not a public key hash
    """
    return _validate(v, prefixes=[b'tz1', b'tz2', b'tz3', b'tz4', b'tz5'])


def validate_l2_pkh(v: Union[str, bytes]):
    """Ensure parameter is a L2 public key hash (starts with b'txr1')

    :param v: string or bytes
    :raises ValueError: if parameter is not a public key hash
    """
    return _validate(v, prefixes=[b'txr1'])


def validate_sig(v: Union[str, bytes]):
    """Ensure parameter is a signature (starts with b'edsig', b'spsig', b'p2sig', b'BLsig', b'sig')

    :param v: string or bytes
    :raises ValueError: if parameter is not a signature
    """
    return _validate(v, prefixes=[b'edsig', b'spsig', b'p2sig', b'BLsig', b'sig'])


def is_pkh(v: Union[str, bytes]) -> bool:
    """Check if value is a public key hash."""
    try:
        validate_pkh(v)
    except (ValueError, TypeError):
        return False
    return True


def is_l2_pkh(v: Union[str, bytes]) -> bool:
    """Check if value is an L2 public key hash."""
    try:
        validate_l2_pkh(v)
    except (ValueError, TypeError):
        return False
    return True


def is_sig(v: Union[str, bytes]) -> bool:
    """Check if value is a signature."""
    try:
        validate_sig(v)
    except (ValueError, TypeError):
        return False
    return True


def is_bh(v: Union[str, bytes]) -> bool:
    """Check if value is a block hash."""
    try:
        _validate(v, prefixes=[b'B'])
    except (ValueError, TypeError):
        return False
    return True


def is_ogh(v) -> bool:
    """Check if value is an operation group hash."""
    try:
        _validate(v, prefixes=[b'o'])
    except (ValueError, TypeError):
        return False
    return True


def is_kt(v: Union[str, bytes]) -> bool:
    """Check if value is a KT address."""
    try:
        _validate(v, prefixes=[b'KT1'])
    except (ValueError, TypeError):
        return False
    return True


def is_sr(v: Union[str, bytes]) -> bool:
    """Check if value is a smart rollup address."""
    try:
        _validate(v, prefixes=[b'sr1'])
    except (ValueError, TypeError):
        return False
    return True


def is_public_key(v: Union[str, bytes]) -> bool:
    """Check if value is a public key."""
    try:
        _validate(
            v,
            prefixes=[
                # ed25519
                b'edsk',
                b'edpk',
                # secp256k1
                b'spsk',
                b'sppk',
                # p256
                b'p2sk',
                b'p2pk',
                # bls12_381
                b'BLsk',
                b'BLpk',
            ],
        )

    except (ValueError, TypeError):
        return False
    return True


def is_chain_id(v: Union[str, bytes]) -> bool:
    """Check if value is a chain id."""
    try:
        _validate(v, prefixes=[b'Net'])
    except (ValueError, TypeError):
        return False
    return True


def is_address(v: Union[str, bytes]) -> bool:
    """Check if value is a tz/KT address"""
    if isinstance(v, bytes):
        v = v.decode()
    address = v.split('%')[0]
    return is_kt(address) or is_pkh(address) or is_sr(address)


def is_txr_address(v: Union[str, bytes]) -> bool:
    """Check if value is a txr1 address"""
    if isinstance(v, bytes):
        v = v.decode()
    address = v.split('%')[0]
    return is_l2_pkh(address)
