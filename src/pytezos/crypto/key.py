import binascii
import hashlib
import json
from getpass import getpass
from hashlib import blake2b
from os import environ as env
from os.path import abspath
from os.path import expanduser
from os.path import join
from typing import List
from typing import Optional
from typing import Union

from mnemonic import Mnemonic

from pytezos.crypto.encoding import base58_decode
from pytezos.crypto.encoding import base58_encode
from pytezos.crypto.encoding import scrub_input
from pytezos.jupyter import InlineDocstring
from pytezos.jupyter import get_class_docstring

VALID_MNEMONIC_LENGTHS = [12, 15, 18, 21, 24]
DEFAULT_LANGUAGE = 'english'
DEFAULT_TEZOS_DIR = '~/.tezos-client'

PassphraseInput = Optional[Union[str, bytes]]


def get_passphrase(passphrase: PassphraseInput = None, alias: Optional[str] = None) -> bytes:
    if passphrase is None:
        passphrase = env.get('PYTEZOS_PASSPHRASE')
    if passphrase is None:
        passphrase = getpass(f'Please enter passphrase{" for key `" + alias + "`" if alias else ""}:\n')
    if passphrase is None:
        raise Exception('Key passphrase is required')
    if isinstance(passphrase, str):
        passphrase = passphrase.encode()
    if not isinstance(passphrase, bytes):
        raise Exception(f'bytes or str expected, got {type(passphrase).__name__}')
    return passphrase


class CryptoExtraFallback:
    def __getattr__(self, item):
        raise ImportError(
            "Please, install packages libsodium-dev, and libgmp-dev, "
            "and Python libraries pysodium, coincurve, and fastecdsa"
        )

    def __call__(self, *args, **kwargs):
        self.__getattr__('throw')


try:
    import coincurve  # type: ignore
    import fastecdsa.curve  # type: ignore
    import fastecdsa.ecdsa  # type: ignore
    import fastecdsa.encoding.sec1  # type: ignore
    import fastecdsa.keys  # type: ignore
    import pysodium  # type: ignore
    from fastecdsa.encoding.util import bytes_to_int  # type: ignore
except ImportError as e:
    coincurve = CryptoExtraFallback()
    pysodium = CryptoExtraFallback()
    fastecdsa = CryptoExtraFallback()
    bytes_to_int = CryptoExtraFallback()
    __crypto__ = False
else:
    __crypto__ = True


def is_installed():
    return __crypto__


def blake2b_32(v=b''):
    """Get a BLAKE2B hash of bytes"""
    return blake2b(scrub_input(v), digest_size=32)


def validate_mnemonic(mnemonic: str, language: str = DEFAULT_LANGUAGE) -> None:
    m = Mnemonic(language)
    mnemonic_words = m.normalize_string(mnemonic).split(' ')
    if len(mnemonic_words) not in VALID_MNEMONIC_LENGTHS:
        raise ValueError(
            'Number of words must be one of the following: {VALID_MNEMONIC_LENGTHS}, '
            'but it is not (%d).' % len(mnemonic_words)
        )

    idx = map(lambda x: bin(m.wordlist.index(x))[2:].zfill(11), mnemonic_words)
    b = ''.join(idx)
    l = len(b)
    d = b[: l // 33 * 32]
    h = b[-l // 33 :]
    nd = binascii.unhexlify(hex(int(d, 2))[2:].rstrip('L').zfill(l // 33 * 8))
    nh = bin(int(hashlib.sha256(nd).hexdigest(), 16))[2:].zfill(256)[: l // 33]
    if h != nh:
        raise ValueError('Mnemonic checksum verification failed')


class Key(metaclass=InlineDocstring):
    """Represents a public or secret key for Tezos. Ed25519, Secp256k1 and P256
    are supported.
    """

    def __init__(
        self,
        public_point: bytes,
        secret_exponent: Optional[bytes] = None,
        curve: bytes = b'ed',
        activation_code: Optional[str] = None,
    ) -> None:
        self.public_point = public_point
        self.secret_exponent = secret_exponent
        self.curve = curve
        self.activation_code = activation_code

    def __repr__(self) -> str:
        res = [
            super().__repr__(),
            '\nPublic key hash',
            self.public_key_hash(),
            '\nHelpers',
            get_class_docstring(self.__class__),
        ]
        return '\n'.join(res)

    @property
    def is_secret(self) -> bool:
        return self.secret_exponent is not None

    @classmethod
    def from_secret_exponent(
        cls,
        secret_exponent: bytes,
        curve=b'ed',
        activation_code=None,
    ) -> 'Key':
        """Creates a key object from a secret exponent.

        :param secret_exponent: secret exponent or seed
        :param curve: b'sp' for Secp251k1, b'p2' for P256/Secp256r1, b'ed' for Ed25519 (default)
        :param activation_code: secret for initializing account balance
        """
        # Ed25519
        if curve == b'ed':
            # Dealing with secret exponent or seed?
            if len(secret_exponent) == 64:
                public_point = pysodium.crypto_sign_sk_to_pk(sk=secret_exponent)
            else:
                public_point, secret_exponent = pysodium.crypto_sign_seed_keypair(seed=secret_exponent)
        # Secp256k1
        elif curve == b'sp':
            sk = coincurve.PrivateKey(secret_exponent)
            public_point = sk.public_key.format(compressed=True)
        # P256
        elif curve == b'p2':
            pk = fastecdsa.keys.get_public_key(bytes_to_int(secret_exponent), curve=fastecdsa.curve.P256)
            public_point = fastecdsa.encoding.sec1.SEC1Encoder.encode_public_key(pk)
        else:
            raise AssertionError()

        return cls(public_point, secret_exponent, curve=curve, activation_code=activation_code)

    @classmethod
    def from_public_point(
        cls,
        public_point: bytes,
        curve: bytes = b'ed',
    ) -> 'Key':
        """Creates a key object from a public elliptic point.

        :param public_point: elliptic point in the compressed format (see https://tezos.stackexchange.com/a/623/309)
        :param curve: b'sp' for secp251k1, b'p2' for P256/secp256r1, b'ed' for Ed25519 (default)
        """
        return cls(public_point, curve=curve)

    @classmethod
    def from_encoded_key(
        cls,
        key: Union[str, bytes],
        passphrase: PassphraseInput = None,
    ) -> 'Key':
        """Creates a key object from a base58 encoded key.

        :param key: a public or secret key in base58 encoding
        :param passphrase: the passphrase used if the key provided is an encrypted private key,
            if not set value from from PYTEZOS_PASSPHRASE env variable will be used or promted dynamically
        """
        encoded_key = scrub_input(key)

        curve = encoded_key[:2]  # "sp", "p2" "ed"
        if curve not in [b'sp', b'p2', b'ed']:
            raise ValueError("Invalid prefix for a key encoding.")
        if not len(encoded_key) in [54, 55, 88, 98]:
            raise ValueError("Invalid length for a key encoding.")

        encrypted = encoded_key[2:3] == b'e'
        public_or_secret = encoded_key[3:5] if encrypted else encoded_key[2:4]
        if public_or_secret not in [b'pk', b'sk']:
            raise Exception("Invalid prefix for a key encoding.")

        encoded_key = base58_decode(encoded_key)
        is_secret = public_or_secret == b'sk'
        if not is_secret:
            return cls.from_public_point(encoded_key, curve)

        if encrypted:
            passphrase = get_passphrase(passphrase)

            salt, encrypted_sk = encoded_key[:8], encoded_key[8:]
            encryption_key = hashlib.pbkdf2_hmac(
                hash_name="sha512",
                password=passphrase,
                salt=salt,
                iterations=32768,
                dklen=32,
            )
            encoded_key = pysodium.crypto_secretbox_open(
                c=encrypted_sk,
                nonce=b'\000' * 24,
                k=encryption_key,
            )
            del passphrase

        return cls.from_secret_exponent(encoded_key, curve)

    @classmethod
    def generate(
        cls,
        passphrase: str = '',
        curve: bytes = b'ed',
        strength: int = 128,
        language: str = DEFAULT_LANGUAGE,
        export: bool = True,
    ):
        """Generates new key.

        :param passphrase: optional password
        :param curve: b'sp' for secp251k1, b'p2' for P256/secp256r1, b'ed' for Ed25519 (default)
        :param strength: mnemonic strength, default is 128
        :param language: mnemonic language, default is english
        :param export: export as json file in the current folder, default is True
        :rtype: Key
        """
        mnemonic = Mnemonic(language).generate(strength)
        key = cls.from_mnemonic(mnemonic, passphrase, curve=curve)

        if export:
            pkh = key.public_key_hash()
            data = {
                'mnemonic': mnemonic.split(),
                'pkh': pkh,
                'password': passphrase or '',
            }
            with open(abspath(f'./{pkh}.json'), 'w+') as f:
                f.write(json.dumps(data))

        return key

    @classmethod
    def from_mnemonic(
        cls,
        mnemonic: Union[List[str], str],
        passphrase: str = '',
        email: str = '',
        validate: bool = True,
        curve: bytes = b'ed',
        activation_code: Optional[str] = None,
        language: str = DEFAULT_LANGUAGE,
    ) -> 'Key':
        """Creates a key object from a bip39 mnemonic.

        :param mnemonic: a 15 word bip39 english mnemonic
        :param passphrase: a mnemonic password or a fundraiser key
        :param email: email used if a fundraiser key is passed
        :param validate: whether to check mnemonic or not
        :param curve: b'sp' for secp251k1, b'p2' for P256/secp256r1, b'ed' for Ed25519 (default)
        :param activation_code: secret for initializing account balance
        :param language: The English label for the language of the mnemonic. This is needed for validation
        :rtype: Key
        """
        if isinstance(mnemonic, list):
            mnemonic = ' '.join(mnemonic)

        if validate:
            validate_mnemonic(mnemonic, language=language)

        seed = Mnemonic.to_seed(mnemonic, passphrase=email + passphrase)

        if curve == b'ed':
            _, secret_exponent = pysodium.crypto_sign_seed_keypair(seed=seed[:32])
        elif curve == b'sp':
            secret_exponent = seed[:32]
        elif curve == b'p2':
            secret_exponent = seed[:32]
        else:
            raise AssertionError()

        return cls.from_secret_exponent(secret_exponent, curve=curve, activation_code=activation_code)

    @classmethod
    def from_faucet(cls, source: Union[str, dict]) -> 'Key':
        """Import key from a faucet file: https://teztnets.xyz/

        :param source: path to the json file
        :rtype: Key
        """
        if isinstance(source, str):
            with open(expanduser(source), 'r') as f:
                data = json.loads(f.read())
        elif isinstance(source, dict):
            data = source
        else:
            raise ValueError(f'Unexpected source {source}')

        key = cls.from_mnemonic(
            mnemonic=data['mnemonic'],
            passphrase=data.get('password', ''),
            email=data.get('email', ''),
            activation_code=data['activation_code'],
        )
        if key.public_key_hash() != data['pkh']:
            raise ValueError('Failed to import')

        return key

    @classmethod
    def from_alias(
        cls,
        alias: str,
        passphrase: PassphraseInput = None,
        tezos_client_dir: str = DEFAULT_TEZOS_DIR,
    ) -> 'Key':
        """Import secret key from tezos-client keychain.

        :param alias: key alias
        :param passphrase: if key is encrypted (optional)
        :param tezos_client_dir: path to the tezos client directory (default is `~/.tezos-client`)
        :rtype: Key
        """
        path = expanduser(join(tezos_client_dir, 'secret_keys'))
        with open(path, 'r') as f:
            data = json.loads(f.read())

        value = next(x['value'] for x in data if x['name'] == alias)
        prefix, sk = value.split(':', maxsplit=1)

        if prefix == 'encrypted':
            passphrase = get_passphrase(passphrase)
            key = cls.from_encoded_key(sk, passphrase=passphrase)
            del passphrase
        else:
            key = cls.from_encoded_key(sk)

        return key

    def public_key(self) -> str:
        """Creates base58 encoded public key representation.

        :returns: the public key associated with the private key
        """
        return base58_encode(self.public_point, self.curve + b'pk').decode()

    def secret_key(
        self,
        passphrase: PassphraseInput = None,
        ed25519_seed: bool = True,
    ):
        """Creates base58 encoded private key representation.

        :param passphrase: encryption phrase for the private key
        :param ed25519_seed: encode seed rather than full key for ed25519 curve (True by default)
        :returns: the secret key associated with this key, if available
        """
        if not self.secret_exponent:
            raise ValueError("Secret key is undefined")

        if self.curve == b'ed' and ed25519_seed:
            key = pysodium.crypto_sign_sk_to_seed(self.secret_exponent)
        else:
            key = self.secret_exponent

        if passphrase:
            if not ed25519_seed:
                raise NotImplementedError
            if isinstance(passphrase, str):
                passphrase = passphrase.encode()
            assert isinstance(passphrase, bytes), f'expected bytes or str, got {type(passphrase).__name__}'

            salt = pysodium.randombytes(8)
            encryption_key = hashlib.pbkdf2_hmac(
                hash_name="sha512",
                password=passphrase,
                salt=salt,
                iterations=32768,
                dklen=32,
            )
            encrypted_sk = pysodium.crypto_secretbox(msg=key, nonce=b'\000' * 24, k=encryption_key)
            key = salt + encrypted_sk  # we have to combine salt and encrypted key in order to decrypt later
            prefix = self.curve + b'esk'
        else:
            prefix = self.curve + b'sk'

        return base58_encode(key, prefix).decode()

    def public_key_hash(self) -> str:
        """Creates base58 encoded public key hash for this key.

        :returns: the public key hash for this key
        """
        pkh = blake2b(self.public_point, digest_size=20).digest()
        prefix = {b'ed': b'tz1', b'sp': b'tz2', b'p2': b'tz3'}[self.curve]
        return base58_encode(pkh, prefix).decode()

    def blinded_public_key_hash(self) -> str:
        """Creates base58 encoded commitment out of activation code (required) and public key hash

        :return: blinded public key hash
        """
        if not self.activation_code:
            raise ValueError("Activation code is undefined")

        pkh = blake2b(self.public_point, digest_size=20).digest()
        key = bytes.fromhex(self.activation_code)
        blinded_pkh = blake2b(pkh, key=key, digest_size=20).digest()
        return base58_encode(blinded_pkh, b'btz1').decode()

    def sign(self, message: Union[str, bytes], generic: bool = False):
        """Sign a raw sequence of bytes.

        :param message: sequence of bytes, raw format or hexadecimal notation
        :param generic: do not specify elliptic curve if set to True
        :returns: signature in base58 encoding
        """
        encoded_message = scrub_input(message)

        if not self.secret_exponent:
            raise ValueError("Cannot sign without a secret key.")

        # Ed25519
        if self.curve == b"ed":
            digest = pysodium.crypto_generichash(encoded_message)
            signature = pysodium.crypto_sign_detached(digest, self.secret_exponent)
        # Secp256k1
        elif self.curve == b"sp":
            pk = coincurve.PrivateKey(self.secret_exponent)
            signature = pk.sign(encoded_message, hasher=lambda x: blake2b_32(x).digest())

        # P256
        elif self.curve == b"p2":
            r, s = fastecdsa.ecdsa.sign(msg=encoded_message, d=bytes_to_int(self.secret_exponent), hashfunc=blake2b_32)
            signature = r.to_bytes(32, 'big') + s.to_bytes(32, 'big')
        else:
            raise AssertionError()

        if generic:
            prefix = b'sig'
        else:
            prefix = self.curve + b'sig'

        return base58_encode(signature, prefix).decode()

    def verify(self, signature: Union[str, bytes], message: Union[str, bytes]) -> bool:
        """Verify signature, raise exception if it is not valid.

        :param message: sequance of bytes, raw format or hexadecimal notation
        :param signature: a signature in base58 encoding
        :raises: ValueError if signature is not valid
        :returns: True if signature is valid
        """
        encoded_signature = scrub_input(signature)
        encoded_message = scrub_input(message)

        if not self.public_point:
            raise ValueError("Cannot verify without a public key")

        if encoded_signature[:3] != b'sig':  # not generic
            if self.curve != encoded_signature[:2]:  # "sp", "p2" "ed"
                raise ValueError("Signature and public key curves mismatch.")

        decoded_signature = base58_decode(encoded_signature)

        # Ed25519
        if self.curve == b"ed":
            digest = pysodium.crypto_generichash(encoded_message)
            try:
                pysodium.crypto_sign_verify_detached(decoded_signature, digest, self.public_point)
            except ValueError as exc:
                raise ValueError('Signature is invalid.') from exc
        # Secp256k1
        elif self.curve == b"sp":
            pk = coincurve.PublicKey(self.public_point)
            if not pk.verify(
                signature=decoded_signature,
                message=encoded_message,
                hasher=lambda x: blake2b_32(x).digest(),
            ):
                raise ValueError('Signature is invalid.')
        # P256
        elif self.curve == b"p2":
            pk = fastecdsa.encoding.sec1.SEC1Encoder.decode_public_key(self.public_point, curve=fastecdsa.curve.P256)
            r, s = bytes_to_int(decoded_signature[:32]), bytes_to_int(decoded_signature[32:])
            if not fastecdsa.ecdsa.verify(sig=(r, s), msg=encoded_message, Q=pk, hashfunc=blake2b_32):
                raise ValueError('Signature is invalid.')
        else:
            raise Exception(f'Unknown elliptic curve {self.curve}')  # type: ignore

        return True
