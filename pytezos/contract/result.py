from typing import List

from pytezos.operation.result import OperationResult
from pytezos.context.impl import ExecutionContext
from pytezos.michelson.program import MichelsonProgram
from pytezos.michelson.types.base import MichelsonType
from pytezos.michelson.types import OperationType


class ContractCallResult(OperationResult):
    """ Encapsulates the result of a contract invocation.
    """

    @classmethod
    def from_run_operation(cls, operation_group: dict, context: ExecutionContext) -> List['ContractCallResult']:
        """ Get a list of results from an operation group content with metadata.

        :param operation_group: {..., "contents": [{..., kind: "transaction", ...}]}
        :param context: execution context
        :rtype: ContractCallResult
        """
        results = list()
        for content in OperationResult.iter_contents(operation_group):
            if content['kind'] == 'transaction':
                if content['destination'] == context.address:
                    results.append(cls.from_transaction(content))
            elif content['kind'] == 'origination':
                result = cls.get_result(content)
                if context.address in result.get('originated_contracts', []):
                    results.append(cls.from_origination(content))

        program = MichelsonProgram.load(context)

        def decode_result(res: OperationResult) -> 'ContractCallResult':
            kwargs = {}
            if hasattr(res, 'storage'):
                storage = program.storage.from_micheline_value(res.storage)
                if hasattr(res, 'lazy_diff'):
                    kwargs.update(lazy_diff=res.lazy_diff)
                    storage = storage.merge_lazy_diff(res.lazy_diff)
                kwargs.update(storage=storage.to_python_object())
            if hasattr(res, 'parameters'):
                parameters = program.parameter.from_parameters(res.parameters)
                kwargs.update(parameters=parameters)
            if hasattr(res, 'operations'):
                kwargs.update(operations=res.operations)
            return cls(**kwargs)

        return list(map(decode_result, results))

    @classmethod
    def from_run_code(cls, response: dict, parameters, context: ExecutionContext):
        """ Parse a result of `run_code` execution.

        :param response: RPC response (json)
        :param parameters: {"entrypoint": str, "value": $Micheline}
        :param context: execution context
        :rtype: ContractCallResult
        """
        program = MichelsonProgram.load(context)
        parameters = program.parameter.from_parameters(parameters)
        storage = program.storage.from_micheline_value(response['storage'])
        extended_storage = storage.merge_lazy_diff(response.get('lazy_diff', []))
        return cls(
            parameters=parameters.to_python_object(),
            storage=extended_storage.to_python_object(lazy_diff=True),
            lazy_diff=response.get('lazy_diff', []),
            operations=response.get('operations', [])
        )

    @classmethod
    def from_repl_result(cls,
                         operations: List[OperationType],
                         storage: MichelsonType,
                         lazy_diff: List[dict],
                         parameters: dict,
                         context: ExecutionContext):
        """ Parse an output of the builtin interpreter.

        :param operations: list of OperationType instances
        :param storage: MichelsonType instance
        :param lazy_diff: [{"kind": "big_map", ...}]
        :param parameters: {"entrypoint": str, "value": $Micheline}
        :param context: execution context
        :rtype: ContractCallResult
        """
        program = MichelsonProgram.load(context)
        extended_storage = storage.merge_lazy_diff(lazy_diff)
        return cls(
            parameters=program.parameter.from_parameters(parameters),
            storage=extended_storage.to_python_object(lazy_diff=True),
            lazy_diff=lazy_diff,
            operations=[op.to_python_object() for op in operations]
        )
