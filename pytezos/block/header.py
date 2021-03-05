from typing import Any, List, Dict, Optional
from pprint import pformat
import bson

from pytezos.context.impl import ExecutionContext  # type: ignore
from pytezos.context.mixin import ContextMixin  # type: ignore
from pytezos.crypto.encoding import base58_encode
from pytezos.crypto.key import blake2b_32
from pytezos.michelson.forge import forge_base58, forge_array
from pytezos.block.forge import forge_protocol_data
from pytezos.jupyter import get_class_docstring


class BlockHeader(ContextMixin):

    def __init__(
        self,
        context: ExecutionContext,
        protocol_data: Optional[Dict[str, Any]] = None,
        operations: Optional[List[dict]] = None,
        protocol: Optional[str] = None,
        signature: Optional[str] = None,
        data: Optional[bytes] = None
    ):
        super().__init__(context=context)
        self.protocol_data = protocol_data or {}
        self.operations = operations or []
        self.protocol = protocol
        self.signature = signature
        self.data = data

    def __repr__(self):
        res = [
            super().__repr__(),
            '\nPayload',
            pformat(self.json_payload()),
            '\nHelpers',
            get_class_docstring(self.__class__)
        ]
        return '\n'.join(res)

    @classmethod
    def activate_protocol(cls, protocol_hash: str, parameters: Dict[str, Any], context: ExecutionContext) \
            -> 'BlockHeader':
        protocol_data = {
            "content": {
                "command": "activate",
                "hash": protocol_hash,
                "fitness": ["00", "0000000000000001"],
                "protocol_parameters": forge_array(bson.dumps(parameters)).hex()
            }
        }
        return BlockHeader(context, protocol_data=protocol_data)

    @classmethod
    def bake_block(cls, min_fee=0) -> 'BlockHeader':
        raise NotImplementedError

    def _spawn(self, **kwargs):
        return BlockHeader(
            context=self.context,
            protocol_data=kwargs.get('protocol_data', self.protocol_data.copy()),
            protocol=kwargs.get('protocol', self.protocol),
            signature=kwargs.get('signature', self.signature),
            data=kwargs.get('data', self.data)
        )

    def fill(self) -> 'BlockHeader':
        """ Fill the protocol field

        :rtype: BlockHeader
        """
        res = self.shell.head.protocols()
        return self._spawn(protocol=res['next_protocol'])

    def json_payload(self) -> dict:
        """Get json payload used for the preapply."""
        signature = self.signature
        if signature is None:
            signature = base58_encode(b'\x00' * 64, b'sig').decode()  # null signature, works for preapply

        return {
            "protocol_data": {
                "protocol": self.protocol,
                **self.protocol_data,
                "signature": signature
            },
            "operations": self.operations
        }

    def binary_payload(self) -> bytes:
        """Get binary payload used for injection/hash calculation."""
        if not self.signature:
            raise ValueError('Not signed')
        return self.data + forge_base58(self.signature)

    def forge(self) -> 'str':
        """Convert json representation of the operation group into bytes.

        :returns: Hex string
        """
        header = self.preapply()
        header['protocol_data'] = forge_protocol_data(self.protocol_data).hex()
        res = self.shell.head.helpers.forge_block_header.post(block_header=header)
        return res['block']

    def sign(self):
        """Sign the operation group with the key specified by `using`.

        :rtype: BlockHeader
        """
        chain_watermark = bytes.fromhex(self.shell.chains.main.watermark())
        watermark = b'\x01' + chain_watermark
        data = bytes.fromhex(self.forge())
        signature = self.key.sign(message=watermark + data)
        return self._spawn(signature=signature, data=data)

    def hash(self) -> str:
        """Calculate the Base58 encoded operation group hash."""
        hash_digest = blake2b_32(self.binary_payload()).digest()
        return base58_encode(hash_digest, b'B').decode()

    def preapply(self):
        """Preapply block

        :returns: shell header and operations
        """
        if self.protocol is None:
            raise ValueError('current protocol is not specified')

        res = self.shell.head.helpers.preapply.block.post(block=self.json_payload())
        # TODO: handle errored operations https://tezos.gitlab.io/alpha/rpc.html#post-block-id-helpers-preapply-block
        return res['shell_header']

    def inject(self, _async=False, force=False):
        """Inject the signed block header.

        :returns: block hash
        """
        block = {
            "data": self.binary_payload().hex(),
            "operations": self.operations
        }
        return self.shell.injection.block.post(block=block, _async=_async, force=force)
