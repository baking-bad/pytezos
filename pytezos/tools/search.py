from typing import Any, Callable, Generator
from loguru import logger
import simplejson as json

from pytezos.rpc.node import RpcError
from pytezos.rpc import mainnet


def find_state_change_intervals(head: int, tail: int, get: Callable, equals: Callable,
                                step=60) -> Generator:
    succ_value = get(head)

    for level in range(head - step, tail, -step):
        value = get(level)
        logger.debug(f'{value} at level {level}')

        if not equals(value, succ_value):
            yield level + step, succ_value, level, value
            succ_value = value


def find_state_change(head: int, tail: int, get: Callable, equals: Callable,
                      pred_value: Any) -> (int, Any):
    def bisect(start: int, end: int):
        if end == start + 1:
            return end, get(end)

        level = (end + start) // 2
        value = get(level)
        logger.debug(f'{value} at level {level}')

        if equals(value, pred_value):
            return bisect(level, end)
        else:
            return bisect(start, level)

    return bisect(tail, head)


def walk_state_change_interval(head: int, tail: int, get: Callable, equals: Callable,
                               head_value: Any, tail_value: Any) -> Generator:
    level = tail
    value = tail_value
    while not equals(value, head_value):
        level, value = find_state_change(
            head, level, get, equals,
            pred_value=value)
        yield level, value


def find_state_changes(head: int, tail: int, get: Callable, equals: Callable,
                       step=60) -> Generator:
    for int_head, int_head_value, int_tail, int_tail_value in find_state_change_intervals(
            head, tail, get, equals, step):
        for change in walk_state_change_interval(
                int_head, int_tail, get, equals,
                head_value=int_head_value,
                tail_value=int_tail_value):
            yield change


class SearchEngine:

    def __init__(self, shell=mainnet):
        self._shell = shell

    def get_voting_period(self):
        level_info = self._shell.head.metadata()['level']
        head = level_info['level']
        tail = head - level_info['voting_period_position']
        return head, tail

    def find_proposal_inject_level(self, proposal_id) -> int:
        level, _ = find_state_change(
            *self.get_voting_period(),
            get=lambda x: self._shell.blocks[x].votes.get_roll_count(proposal_id),
            equals=lambda x, y: x == y,
            pred_value=0
        )
        return level

    def find_proposal_votes_levels(self, proposal_id) -> Generator:
        for level, _ in find_state_changes(
                *self.get_voting_period(),
                get=lambda x: self._shell.blocks[x].votes.get_roll_count(proposal_id),
                equals=lambda x, y: x == y):
            yield level

    def find_proposal_inject_operation(self, proposal_id):
        level = self.find_proposal_inject_level(proposal_id)
        operations = self._shell.blocks[level].operations.votes()
        if not operations:
            raise ValueError('Injection operation not found.')

        return operations[0]

    def find_proposal_votes_operations(self, proposal_id) -> Generator:
        for level in self.find_proposal_votes_levels(proposal_id):
            for operation in self._shell.blocks[level].operations.votes():
                yield operation

    def find_contract_origination_level(self, contract_id) -> int:
        def get_counter(x):
            try:
                return self._shell.blocks[x].context.contracts[contract_id].counter()
            except RpcError:
                return None

        level, _ = find_state_change(
            head=self._shell.head.get_level(),
            tail=0,
            get=get_counter,
            equals=lambda x, y: x == y,
            pred_value=None
        )
        return level

    def find_contract_origination_operation(self, contract_id):
        level = self.find_contract_origination_level(contract_id)
        operations = self._shell.blocks[level].operations.managers()

        # TODO: flat operations
        # for operation in operations:
        #     for content in filter_contents(operation, kind='origination'):
        #         if content.get('metadata'):
        #             result = content['metadata']['operation_result']
        #         else:
        #             result = content['result']
        #         if contract_id in result['originated_contracts']:
        #             return operation

        raise ValueError('Origination operation not found.')

    def find_storage_change_levels(self, contract_id, origination_level=None) -> Generator:
        if origination_level is None:
            origination_level = self.find_contract_origination_level(contract_id)

        for level, _ in find_state_changes(
                head=self._shell.head.get_level(),
                tail=origination_level,
                get=lambda x: hash(json.dumps(self._shell.blocks[x].context.contracts[contract_id].storage())),
                equals=lambda x, y: x == y,
                step=720):
            yield level

    def find_storage_change_operations(self, contract_id, origination_level=None) -> Generator:
        for level in self.find_storage_change_levels(contract_id, origination_level):
            for operation in self._shell.blocks[level].operations.managers():
                if any(map(lambda x: x.get('destination') == contract_id, operation['contents'])):
                    yield operation
