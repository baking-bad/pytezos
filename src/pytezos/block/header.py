import itertools
from pprint import pformat
from typing import Any
from typing import Dict
from typing import List
from typing import Optional

import simple_bson as bson  # type: ignore

from pytezos.block.forge import bump_fitness
from pytezos.block.forge import forge_block_header
from pytezos.block.forge import forge_protocol_data
from pytezos.context.impl import ExecutionContext
from pytezos.context.mixin import ContextMixin
from pytezos.crypto.encoding import base58_encode
from pytezos.crypto.hash import block_payload_hash
from pytezos.crypto.key import blake2b_32
from pytezos.jupyter import get_class_docstring
from pytezos.michelson.forge import forge_array
from pytezos.michelson.forge import forge_base58
from pytezos.michelson.forge import optimize_timestamp
from pytezos.rpc.kind import validation_passes
from pytezos.sandbox.parameters import protocol_version
from pytezos.sandbox.parameters import sandbox_params

bson.encoder.encoders[int] = bson.encoder.encoders[float]


class BlockHeader(ContextMixin):
    """Representation of block creation call"""

    def __init__(
        self,
        context: ExecutionContext,
        protocol_data: Optional[Dict[str, Any]] = None,
        operations: Optional[List[List[Dict[str, Any]]]] = None,
        shell_header: Optional[Dict[str, Any]] = None,
        signature: Optional[str] = None,
    ) -> None:
        super().__init__(context=context)
        self.protocol_data = protocol_data or {}
        self.operations = operations or []
        self.shell_header = shell_header or {}
        self.signature = signature

    def __repr__(self) -> str:
        res = [
            super().__repr__(),
            '\nHeader',
            pformat(
                {
                    **self.shell_header,
                    'protocol_data': {
                        **self.protocol_data,
                        'signature': self.signature,
                    },
                }
            ),
            '\nOperations',
            pformat(self.operations),
            '\nHelpers',
            get_class_docstring(self.__class__),
        ]
        return '\n'.join(res)

    @classmethod
    def activate_protocol(
        cls,
        protocol_hash: str,
        parameters: Dict[str, Any],
        context: ExecutionContext,
    ) -> 'BlockHeader':
        """Create call to bake genesis block with specified parameters

        :param protocol_hash: protocol hash (ex. PsFLorenaUUuikDWvMDr6fGBRG8kt3e3D3fHoXK1j1BFRxeSH4i)
        :param parameters: protocol parameters
        :param context: execution context
        """
        # FIXME: Rio bson fixup
        if parameters.get('all_bakers_attest_activation_level', '') is None:
            parameters['all_bakers_attest_activation_level'] = 0

        prev_fitness = context.shell.head.header()['fitness']  # type: ignore
        protocol_data = {
            "content": {
                "command": "activate",
                "hash": protocol_hash,
                "fitness": bump_fitness(prev_fitness),
                "protocol_parameters": forge_array(bson.dumps(parameters)).hex(),
            }
        }
        return BlockHeader(
            context=context,
            protocol_data=protocol_data,
        )

    @classmethod
    def bake_block(cls, context: ExecutionContext, min_fee: int = 0) -> 'BlockHeader':
        """Create call to bake new block

        :param context: Execution context
        :param min_fee: Minimum fee of transaction to be included in block
        """
        pending_operations = context.shell.mempool.pending_operations()  # type: ignore
        operations: List[List[Dict[str, Any]]] = [[], [], [], []]

        for opg in pending_operations['validated']:
            validation_pass = validation_passes[opg['contents'][0]['kind']]
            if validation_pass == 3 and sum(map(lambda x: int(x['fee']), opg['contents'])) < min_fee:
                continue
            operations[validation_pass].append(opg)

        # NOTE: Real values will be set during fill
        protocol_data = {
            "proof_of_work_nonce": "0000000000000000",
            "payload_hash": "vh1g87ZG6scSYxKhspAUzprQVuLAyoa5qMBKcUfjgnQGnFb3dJcG",  # dummy payload (zeroes)
            "payload_round": 0,
            "liquidity_baking_toggle_vote": "off",
            "adaptive_issuance_vote": "off",
        }

        return BlockHeader(
            context=context,
            operations=operations,
            protocol_data=protocol_data,
        )

    def _spawn(self, **kwargs):
        return BlockHeader(
            context=self.context,
            protocol_data=kwargs.get('protocol_data', self.protocol_data.copy()),
            operations=kwargs.get('operations', self.operations.copy()),
            shell_header=kwargs.get('shell_header', self.shell_header.copy()),
            signature=kwargs.get('signature', self.signature),
        )

    def fill(self, timestamp: Optional[int] = None) -> 'BlockHeader':
        """Fill missing fields essential for preapply

        :param timestamp: override header timestamp (unix seconds).
            NOTE that the minimal block granularity in Tezos is 1 sec, so you cannot bake faster that once per second.
            You also cannot bake with timestamp in the future, it will end with error.
            The workaround is to set the genesis block timestamp to zero (or very old date)
            so that you can continuously increase it by 1 sec.
        :rtype: BlockHeader
        """
        pred_shell_header = self.shell.head.header.shell()
        if timestamp is None:
            timestamp = optimize_timestamp(pred_shell_header['timestamp']) + 1
        protocol = self.shell.head.protocols()['next_protocol']
        level = int(pred_shell_header['level']) + 1
        dummy_signature = base58_encode(b'\x00' * 64, b'sig').decode()

        protocol_data = {
            'protocol': protocol,
            **self.protocol_data,
        }

        # NOTE: Tallinn (024) removed adaptive_issuance_vote from block headers
        if protocol_version.get(protocol, 0) >= 24:
            protocol_data.pop('adaptive_issuance_vote', None)

        if level % int(sandbox_params['blocks_per_commitment']) == 0:
            protocol_data['seed_nonce_hash'] = base58_encode(b'\x00' * 32, b'nce').decode()

        operations = [
            [
                {
                    'protocol': protocol,
                    'branch': operation['branch'],
                    'contents': operation['contents'],
                    'signature': operation['signature'],
                }
                for operation in operation_list
            ]
            for operation_list in self.operations
        ]

        payload = {
            'protocol_data': {
                **protocol_data,
                'signature': dummy_signature,
            },
            'operations': operations,
        }

        res = self.shell.head.helpers.preapply.block.post(
            block=payload,
            sort=True,
            timestamp=timestamp,
        )

        forged_operations = [
            [
                {
                    'branch': operation['branch'],
                    'data': operation['data'],
                }
                for operation in operation_list['applied']
            ]
            for operation_list in res['operations']
        ]

        if 'payload_hash' in protocol_data:
            operation_hashes = [
                [operation['hash'] for operation in operation_list['applied']]
                for operation_list in res['operations'][1:]  # skip consensus ops
            ]
            protocol_data['payload_hash'] = block_payload_hash(
                predecessor=res['shell_header']['predecessor'],
                payload_round=protocol_data['payload_round'],
                operation_hashes=list(itertools.chain(*operation_hashes)),
            )

        return self._spawn(
            shell_header=res['shell_header'],
            operations=forged_operations,
            protocol_data=protocol_data,
            signature=dummy_signature,
        )

    def work(self) -> 'BlockHeader':
        """Perform calculations to find proof-of-work nonce"""
        header = self
        threshold = int(sandbox_params['proof_of_work_threshold'])
        nonce = 1

        while header.pow_stamp() > threshold:
            header = self._spawn(
                protocol_data={
                    **self.protocol_data,
                    'proof_of_work_nonce': nonce.to_bytes(8, 'big').hex(),
                }
            )
            nonce += 1

        return header

    def binary_payload(self) -> bytes:
        """Get binary payload used for injection/hash calculation."""
        if self.signature is None:
            raise ValueError('Not signed')
        return self.forge() + forge_base58(self.signature)

    def forge(self) -> bytes:
        """Convert json representation of the block header into bytes.

        :returns: Binary payload (unsigned)
        """
        return forge_block_header(
            {
                **self.shell_header,
                'protocol_data': forge_protocol_data(self.protocol_data).hex(),
            }
        )

    def pow_stamp(self) -> int:
        data = self.forge() + b'\x00' * 64
        hash_digest = blake2b_32(data).digest()
        return int.from_bytes(hash_digest[:8], 'big')

    def hash(self) -> str:
        hash_digest = blake2b_32(self.binary_payload()).digest()
        return base58_encode(hash_digest, b'B').decode()

    def sign(self) -> 'BlockHeader':
        """Sign the block header with the key specified by `using`.

        :rtype: BlockHeader
        """
        chain_watermark = bytes.fromhex(self.shell.chains.main.watermark())
        proto = protocol_version.get(self.protocol_data['protocol'], 0)
        if proto >= 12:  # since Ithaca
            watermark = b'\x11' + chain_watermark
        else:
            watermark = b'\x01' + chain_watermark
        payload = self.forge()
        signature = self.key.sign(message=watermark + payload)
        return self._spawn(signature=signature)

    def inject(self, force=False) -> str:
        """Inject the signed block header.

        :returns: block hash
        """
        payload = {
            "data": self.binary_payload().hex(),
            "operations": self.operations,
        }
        return self.shell.injection.block.post(
            block=payload,
            _async=False,
            force=force,
        )
