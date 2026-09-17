from binascii import hexlify
from datetime import datetime
from datetime import timezone
from functools import cached_property
from functools import lru_cache
from time import sleep
from typing import Any
from typing import Dict
from typing import Generator
from typing import List
from typing import Optional

import requests
import simplejson as json
from deprecation import deprecated  # type: ignore

from pytezos.crypto.encoding import base58_decode
from pytezos.jupyter import get_attr_docstring
from pytezos.logging import logger
from pytezos.rpc.kind import validation_passes
from pytezos.rpc.node import RpcForbiddenError
from pytezos.rpc.node import RpcNotFoundError
from pytezos.rpc.protocol import BlockQuery
from pytezos.rpc.protocol import BlocksQuery
from pytezos.rpc.query import RpcQuery
from pytezos.rpc.search import CyclesQuery
from pytezos.rpc.search import VotingPeriodsQuery

MAX_BLOCK_TIMEOUT = 86400


def make_operation_result(**kwargs):
    return {'metadata': {'operation_result': kwargs}}


class ShellQuery(RpcQuery, path=''):
    @property
    def blocks(self) -> BlocksQuery:
        """Shortcut for `chains.main.blocks`"""
        return self.chains.main.blocks

    @property
    def head(self) -> BlockQuery:
        """Shortcut for `blocks.head`"""
        return self.blocks.head

    @cached_property
    def block(self) -> BlockQuery:
        """Cached head block, useful if you just want to explore things."""
        return self.blocks[self.head.hash()]

    @property
    def cycles(self):
        """Operate on cycles rather than blocks."""
        return CyclesQuery(
            node=self.node,
            path=self._wild_path + '/chains/{}/blocks',
            params=self._params + ['main'],
        )

    @property
    def voting_periods(self):
        """
        Operate on voting periods rather than blocks.
        """
        return VotingPeriodsQuery(
            node=self.node,
            path=self._wild_path + '/chains/{}/blocks',
            params=self._params + ['main'],
        )

    @property
    def contracts(self):
        """Shortcut for `head.context.contracts`"""
        return self.head.context.contracts

    @property
    def mempool(self):
        """Shortcut for `chains.main.mempool`"""
        return self.chains.main.mempool

    def wait_blocks(
        self,
        current_block_hash: str,
        max_blocks: int = 1,
        yield_current=False,
        time_between_blocks: Optional[int] = None,
        block_timeout: Optional[int] = None,
    ) -> Generator[str, None, None]:
        """Iterates over future blocks (waits and yields block hash), handles reorgs

        :param current_block_hash: hash of the current block (head)
        :param max_blocks: number of blocks to iterate (not including the current one)
        :param yield_current: yield current block hash at the very beginning
        :param time_between_blocks: override protocol constant
        :param block_timeout: set block timeout (by default Pytezos will wait for a long time)
        :return: block hashes
        """
        if time_between_blocks is None:
            constants = self.blocks[current_block_hash].context.constants()
            time_between_blocks = int(constants.get('minimal_block_delay', 0))

        if block_timeout is None:
            block_timeout = MAX_BLOCK_TIMEOUT

        if yield_current:
            yield current_block_hash

        current_header = self.blocks[current_block_hash].header()
        max_level = current_header['level'] + max_blocks

        while current_header['level'] < max_level:
            logger.info('Current level: %d (max %d)', current_header['level'], max_level)
            prev_block_dt = datetime.strptime(current_header['timestamp'], '%Y-%m-%dT%H:%M:%SZ').replace(
                tzinfo=timezone.utc
            )
            elapsed_sec = (datetime.now(timezone.utc) - prev_block_dt).seconds
            sleep_sec = 1 if elapsed_sec > time_between_blocks else (time_between_blocks - elapsed_sec + 1)

            logger.info('Sleep %d seconds until block %s is superseded', sleep_sec, current_block_hash)
            sleep(sleep_sec)

            next_block_hash: Optional[str] = None

            for delay in range(block_timeout):
                next_block_hash = self.head.hash()
                if current_block_hash == next_block_hash:
                    sleep(1)
                else:
                    logger.info('Found new block %s (%d sec delay)', next_block_hash, delay)
                    break

            if current_block_hash != next_block_hash:
                assert next_block_hash
                yield next_block_hash
                current_block_hash = next_block_hash
                current_header = self.blocks[current_block_hash].header()
            else:
                raise TimeoutError('Reached timeout (%d sec) while waiting for the next block', block_timeout)

    def wait_operations(
        self,
        opg_hashes: List[str],
        ttl: int,
        min_confirmations: int,
        current_block_hash: Optional[str] = None,
        time_between_blocks: Optional[int] = None,
        block_timeout: Optional[int] = None,
    ) -> List[dict]:
        """Wait for one or many operations gain enough confirmations

        :param opg_hashes: list of operation hashes
        :param ttl: max time-to-live value (in mempool)
        :param min_confirmations: minimum number of blocks after inclusion to wait for
        :param current_block_hash: current block hash (head)
        :param time_between_blocks: override protocol constant
        :param block_timeout: set block timeout (by default Pytezos will wait for a long time)
        :return: list of operation contents with metadata
        """

        confirmations = {}
        pending = set(opg_hashes)
        operations = []
        block_hash = current_block_hash

        if block_hash is None:
            block_hash = self.head.hash()

        for block_hash in self.wait_blocks(  # noqa: B020
            current_block_hash=block_hash,
            max_blocks=ttl,
            yield_current=True,
            time_between_blocks=time_between_blocks,
            block_timeout=block_timeout,
        ):
            if len(pending) > 0:
                mempool = set(map(lambda x: x['hash'], self.mempool.pending_operations.flatten()))
                for opg_hash in opg_hashes:
                    if opg_hash in pending:
                        if opg_hash in mempool:
                            logger.info('Operation %s is still in mempool', opg_hash)
                        else:
                            logger.info('Operation %s has left mempool', opg_hash)
                            pending.remove(opg_hash)

            included = self.blocks[block_hash].operation_hashes()
            for i, vp in enumerate(included):
                for j, opg_hash in enumerate(vp):
                    if opg_hash in opg_hashes and opg_hash not in confirmations:
                        logger.info('Operation %s has been included to block %s', opg_hash, block_hash)
                        if opg_hash in pending:  # can be still in the particular node's mempool (not yet removed)
                            pending.remove(opg_hash)
                        confirmations[opg_hash] = 0  # initialize
                        operations.append(self.blocks[block_hash].operations[i][j]())

            for opg_hash in confirmations:
                confirmations[opg_hash] += 1
                logger.info(
                    'Operation %s has %d/%d confirmations', opg_hash, confirmations[opg_hash], min_confirmations
                )

            if len(operations) == len(opg_hashes):
                break

        if len(operations) < len(opg_hashes):
            raise StopIteration('Only %d of %d operations were included, stopping' % (len(operations), len(opg_hashes)))

        for _ in self.wait_blocks(
            block_hash,
            max_blocks=min_confirmations - 1,
            time_between_blocks=time_between_blocks,
        ):
            for opg_hash in opg_hashes:
                confirmations[opg_hash] += 1
                logger.info(
                    'Operation %s has %d/%d confirmations', opg_hash, confirmations[opg_hash], min_confirmations
                )

        return operations

    @deprecated(deprecated_in='3.2.2', removed_in='4.0.0', details=f'Use wait_blocks() instead')
    def wait_next_block(
        self,
        delay_sec=1,
        prev_hash=None,
        time_between_blocks: Optional[int] = None,
        max_iterations: Optional[int] = None,
    ):
        """Wait until next block is finalized.

        :param prev_hash: Current block hash (optional). If not set, current head is used.
        :param time_between_blocks: override the corresponding parameter from constants
        :param max_iterations: Manually set the number of iterations
        :param delay_sec: Sleep delay
        """
        if time_between_blocks is None:
            time_between_blocks = int(self.block.context.constants()["minimal_block_delay"])  # type: ignore

        if time_between_blocks > 0:
            if prev_hash is None:
                header = self.head.header()
                prev_hash = header['hash']
                prev_block_dt = datetime.strptime(header['timestamp'], '%Y-%m-%dT%H:%M:%SZ')
                elapsed_sec = (datetime.utcnow() - prev_block_dt).seconds
                sleep_sec = 0 if elapsed_sec > time_between_blocks else time_between_blocks - elapsed_sec
            else:
                sleep_sec = time_between_blocks
            logger.info('Wait %s seconds until block %s is finalized', sleep_sec, prev_hash)
            sleep(sleep_sec)

        if max_iterations is None:
            max_iterations = max(1, time_between_blocks)

        for _ in range(max_iterations):
            current_block_hash = self.head.hash()
            if current_block_hash == prev_hash:
                sleep(delay_sec)
            else:
                return current_block_hash
        raise StopIteration("Timeout")

    def get_confirmations(self, opg_hash, kind, branch, head) -> int:
        """Returns the number of blocks applied after the operation was included in chain

        :param opg_hash: Operation group hash
        :param kind: Operation kind ('transaction', 'origination', etc)
        :param branch: Block ID one should stop the search at
        :param head: Block ID one should start the search from
        :return: Number of confirmations (0 if not found)
        """
        start = self.blocks[head].header()['level']
        stop = self.blocks[branch].header()['level']
        for level in range(start, stop, -1):
            vp = validation_passes[kind]
            hashes = self.blocks[level].operation_hashes[vp]()
            for idx, _hash in enumerate(hashes):
                if opg_hash == _hash:
                    _ = self.blocks[level].operations[vp, idx]()
                    logger.info('Operation %s was included in block %s', opg_hash, level)
                    return start - level + 1
        return 0


class ChainQuery(RpcQuery, path='/chains/{}'):
    def watermark(self):
        """Chain watermark, hex encoded."""
        data = self.chain_id()
        return hexlify(base58_decode(data.encode())).decode()


class InvalidBlockQuery(RpcQuery, path='/chains/{}/invalid_blocks/{}'):
    def delete(self):
        return self._delete()


class MempoolQuery(RpcQuery, path='/chains/{}/mempool'):
    def post(self, configuration):
        """Set operation filter rules.

        :param configuration: a JSON dictionary, known keys are `minimal_fees`, `minimal_nanotez_per_gas_unit`,
            `minimal_nanotez_per_byte`
        """
        return self._post(json=configuration)


class PendingOperationsQuery(RpcQuery, path='/chains/{}/mempool/pending_operations'):
    def __getitem__(self, item: str) -> Dict[str, Any]:
        """Search for operation in node's mempool by hash.

        :param item: operation group hash (base58)
        """
        operations_dict = self()
        for status, operations in operations_dict.items():
            for operation in operations:
                if isinstance(operation, dict):
                    if operation['hash'] == item:
                        return {
                            **make_operation_result(status=status),
                            **operation,
                        }
                elif isinstance(operation, list):
                    if operation[0] == item:
                        errors = operation[1].pop1('error', default=[])
                        return {
                            **make_operation_result(status=status, errors=errors),
                            **operation[1],
                            'hash': operation[0],
                        }
                else:
                    raise Exception('Unknown operation type', operation)
        raise StopIteration

    def flatten(self) -> List[Dict[str, Any]]:
        operations_dict = self()
        operations_list = []
        for status, operations in operations_dict.items():
            for operation in operations:
                if isinstance(operation, dict):
                    operations_list.append(
                        {
                            **make_operation_result(status=status),
                            **operation,
                        }
                    )
                elif isinstance(operation, list):
                    errors = operation[1].pop('error', [])
                    operations_list.append(
                        {
                            **make_operation_result(status=status, errors=errors),
                            **operation[1],
                            'hash': operation[0],
                        }
                    )
                else:
                    raise Exception('Unknown operation type', operation)
        return operations_list

    def from_source(self, source: str) -> List[Dict[str, Any]]:
        """Contents of operations from `source` that are still waiting for inclusion (validated or not yet processed).
        Empty when the node has no mempool or does not expose it.

        :param source: public key hash
        """
        try:
            operations_dict = self(
                source=source,
                refused='false',
                outdated='false',
                branch_refused='false',
                branch_delayed='false',
            )
        except (RpcForbiddenError, RpcNotFoundError) as e:
            logger.debug('mempool is not available (%s), assuming no pending operations', e)
            return []
        validated = operations_dict.get('validated', operations_dict.get('applied', []))
        contents = []
        for operation in validated + operations_dict.get('unprocessed', []):
            if isinstance(operation, list):
                operation = operation[1]
            for content in operation.get('contents', []):
                if content.get('source') == source:
                    contents.append(content)
        return contents

    def __repr__(self):
        res = [
            super(PendingOperationsQuery, self).__repr__(),
            '[]' + get_attr_docstring(self.__class__, '__getitem__'),
            '.from_source()' + get_attr_docstring(self.__class__, 'from_source'),
        ]
        return '\n'.join(res)


class DescribeQuery(RpcQuery, path='/describe'):
    def __call__(self, recurse=True):
        """Get RPCs documentation and input/output schema.

        :param recurse: Show information for child elements, default is True.
            In some cases doesn't work without this flag.
        """
        return super().__call__(recurse=recurse)

    def __repr__(self):
        res = [
            super().__repr__(),
            f'(){get_attr_docstring(DescribeQuery, "__call__")}',
            'Can be followed by any path:\n.chains\n.network.connections\netc\n',
        ]
        return '\n'.join(res)


class BlockInjectionQuery(RpcQuery, path='/injection/block'):
    def post(self, block, timestamp=None, _async=False, force=False, chain=None):
        """Inject a block in the node and broadcast it.

        The `operations` embedded in `blockHeader` might be pre-validated using a contextual RPCs from the latest block
        (e.g. '/blocks/head/context/preapply').

        block format:

        .. code-block:: python

            {
                "data": <hex-encoded block header>,
                "operations": [ [ {
                "branch": <block_hash>,
                "data": <hex-encoded operation>
                } ... ] ... ]
            }

        :param block: JSON input
        :param _async: By default, the RPC will wait for the block to be validated before answering, \
        set True if you don't want to.
        :param force:
        :param chain: Optionally you can specify the chain (main/test)
        :returns: ID of the block
        """
        return self._post(
            params={
                'async': _async,
                'force': force,
                'chain': chain,
                'timestamp': timestamp,
            },
            json=block,
        )


class OperationInjectionQuery(RpcQuery, path='/injection/operation'):
    def post(self, operation, _async=False, chain=None):
        """Inject an operation in node and broadcast it.
        The `signedOperationContents` should be constructed using a contextual RPCs from the latest block
        and signed by the client.

        :param operation: Hex-encoded operation data or bytes
        :param _async: By default, the RPC will wait for the operation to be (pre-)validated before answering,
            set True if you don't want to.
        :param chain: Optionally you can specify the chain
        :returns: ID of the operation
        """
        if isinstance(operation, bytes):
            operation = operation.hex()

        return self._post(
            params={
                'async': _async,
                'chain': chain,
            },
            json=operation,
        )


class ProtocolInjectionQuery(RpcQuery, path='/injection/protocol'):
    def post(self, protocol, _async=False, force=False):
        """Inject a protocol in node.

        protocol format:

        .. code-block:: python

            {
                "expected_env_version": <integer>,
                "components": [{
                    "name": <unistring>,
                    "interface"?: <hex-encoded data>,
                    "implementation": <hex-encoded data> }
                     ...
                ]}
            }

        :param protocol: JSON input
        :param _async:
        :param force:
        :returns: ID of the protocol
        """
        return self._post(
            params={
                'async': _async,
                'force': force,
            },
            json=protocol,
        )


class ResponseGenerator:
    def __init__(self, res: requests.Response):
        self._lines = res.iter_lines()

    def __iter__(self):
        for line in self._lines:
            yield json.loads(line.decode())


class MonitorQuery(
    RpcQuery,
    path=[
        '/monitor/active_chains',
        '/monitor/bootstrapped',
        '/monitor/commit_hash',
        '/monitor/heads/{}',
        '/monitor/protocols',
        '/monitor/valid_blocks',
    ],
):
    def __call__(self, *args, **kwargs):
        return ResponseGenerator(
            self.node.request(
                method='GET',
                path=self.path,
                params=kwargs,
                stream=True,
            )
        )

    def __repr__(self):
        res = [
            super().__repr__(),
            'NOTE: Returned object is a generator.',
        ]
        return '\n'.join(res)


class ConnectionQuery(RpcQuery, path='/network/connections/{}'):
    def delete(self, wait=False):
        return self._delete(params={'wait': wait})


class NetworkItems(RpcQuery, path=['/network/peers', '/network/points']):
    def __call__(self, _filter=None):
        return self._get(params={'filter': _filter})


class NetworkLogQuery(RpcQuery, path=['/network/peers/{}/log', '/network/points/{}/log']):
    def __call__(self, monitor=False):
        if monitor:
            return ResponseGenerator(
                self.node.request(
                    method='GET',
                    path=self.path,
                    stream=True,
                )
            )
        return self._get()
