import logging
from os import listdir
from os.path import dirname
from os.path import join
from unittest.case import TestCase

from pytezos.logging import logger
from pytezos.michelson.parse import MichelsonParser
from pytezos.michelson.parse import michelson_to_micheline
from pytezos.michelson.repl import Interpreter


class TztTest(TestCase):
    path = join(dirname(__file__), "tzt")
    exclude = {
        ".git",
        "LICENSE",
        "NOTICE",
        "LICENSES",
        "coverage.md",
        "README.md",
        "macro_pack",
        "legacy",
        #
        "add_00.tc.tzt",
        "add_01.tc.tzt",
        # NOTE: unknown primitive `MutezOverflow`
        "add_mutez-mutez_01.tzt",
        # NOTE: unknown primitive `Contract`
        "address_00.tc.tzt",
        "address_00.tzt",
        "address_02.tzt",
        "and_bytes-bytes_00.tzt",
        "and_bytes-bytes_01.tzt",
        "and_bytes-bytes_02.tzt",
        "and_bytes-bytes_03.tzt",
        "car_00.tc.tzt",
        "cdr_00.tc.tzt",
        "checksignature_00.tc.tzt",
        "compare_00.tc.tzt",
        "compare_01.tc.tzt",
        "compare_02.tc.tzt",
        "cons_lists_00.tc.tzt",
        "contract_00.tzt",
        "contract_01.tzt",
        "contract_02.tzt",
        "contract_03.tzt",
        "contract_04.tzt",
        "contract_05.tzt",
        # NOTE: unknown primitive `Failed`
        "failwith_00.tc.tzt",
        "failwith_00.tzt",
        "get_00.tc.tzt",
        "get_map_00.tc.tzt",
        "gt_00.tc.tzt",
        "if_00.tc.tzt",
        "if_01.tc.tzt",
        "ifcons_00.tc.tzt",
        "ifleft_00.tc.tzt",
        "ifnone_00.tc.tzt",
        "int_00.tc.tzt",
        "iter_00.tc.tzt",
        "loop_00.tc.tzt",
        "loop_01.tc.tzt",
        # NOTE: unknown primitive `GeneralOverflow`
        "lsl_01.tzt",
        # NOTE: unknown primitive `GeneralOverflow`
        "lsr_01.tzt",
        # NOTE: unknown primitive `MutezOverflow`
        "mul_mutez-nat_01.tzt",
        # NOTE: unknown primitive `MutezOverflow`
        "mul_nat-mutez_01.tzt",
        # NOTE: MichelsonRuntimeError: ('NOT', 'unexpected types `bytes`')
        "not_bytes_00.tzt",
        "not_bytes_01.tzt",
        "not_bytes_02.tzt",
        "not_bytes_03.tzt",
        "not_bytes_04.tzt",
        "not_bytes_05.tzt",
        # NOTE: parameter type is not defined
        "self_00.tzt",
        "self_in_lambda.tc.tzt",
        # NOTE: failed to parse expression LexToken(_,'_',1,199)
        "concat_00.tc.tzt",
        "createcontract_00.tzt",
        "createcontract_01.tzt",
        "dip_00.tc.tzt",
        "emptyset_00.tc.tzt",
        "dipn_00.tc.tzt",
        "dipn_01.tc.tzt",
        "dipn_02.tc.tzt",
        "drop_00.tc.tzt",
        "dropn_00.tc.tzt",
        "dup_00.tc.tzt",
        "dupn_00.tc.tzt",
        "dupn_01.tc.tzt",
        "pack_operation_00.tc.tzt",
        "pair_00.tc.tzt",
        "push_00.tc.tzt",
        "setdelegate_00.tc.tzt",
        "setdelegate_00.tzt",
        "never_00.tc.tzt",
        "transfertokens_00.tc.tzt",
        "transfertokens_00.tzt",
        "transfertokens_01.tzt",
        "unpair_00.tc.tzt",
        "update_00.tc.tzt",
        "update_bigmapstringstring_01.tzt",
        "update_bigmapstringstring_02.tzt",
        "update_bigmapstringstring_03.tzt",
        "update_bigmapstringstring_04.tzt",
        "update_bigmapstringstring_05.tzt",
        "update_bigmapstringstring_06.tzt",
        "update_bigmapstringstring_07.tzt",
        "xor_bytes-bytes_00.tzt",
        "xor_bytes-bytes_01.tzt",
        "xor_bytes-bytes_02.tzt",
        "xor_bytes-bytes_03.tzt",
        # NOTE: ('SLICE', 'string is empty')
        "slice_string_05.tzt",
        "some_00.tc.tzt",
        # NOTE: unknown primitive `MutezUnderflow`
        "sub_mutez-mutez_01.tzt",
        "swap_00.tc.tzt",
        "swap_01.tc.tzt",
        # NOTE: MichelsonRuntimeError: ('LSL', 'expected nat, got bytes at ``')
        "lsl_bytes_00.tzt",
        "lsl_bytes_02.tzt",
        "lsl_bytes_03.tzt",
        "lsl_bytes_04.tzt",
        "lsl_bytes_05.tzt",
        "lsl_bytes_06.tzt",
        # NOTE: MichelsonRuntimeError: ('LSR', 'expected nat, got bytes at ``')
        "lsr_bytes_00.tzt",
        "lsr_bytes_01.tzt",
        "lsr_bytes_02.tzt",
        "lsr_bytes_03.tzt",
        "lsr_bytes_04.tzt",
        "lsr_bytes_05.tzt",
        "lsr_bytes_06.tzt",
        "lsr_bytes_07.tzt",
        # NOTE: MichelsonRuntimeError: ('OR'/'AND'/'XOR', 'unexpected types `bytes * bytes`')
        "and_bytes-bytes_04.tzt",
        "and_bytes-bytes_05.tzt",
        "and_bytes-bytes_06.tzt",
        "or_bytes-bytes_00.tzt",
        "or_bytes-bytes_01.tzt",
        "or_bytes-bytes_02.tzt",
        "or_bytes-bytes_03.tzt",
        "or_bytes-bytes_04.tzt",
        "or_bytes-bytes_05.tzt",
        "or_bytes-bytes_06.tzt",
        "xor_bytes-bytes_04.tzt",
        "xor_bytes-bytes_05.tzt",
        "xor_bytes-bytes_06.tzt",
        # NOTE: MichelsonRuntimeError: ('Stack_elt', '`option` is neither pushable nor big_map')
        "join_tickets_00.tzt",
        "join_tickets_01.tzt",
        "join_tickets_02.tzt",
        "join_tickets_03.tzt",
        "read_ticket_00.tzt",
        "ticket_00.tzt",
        "ticket_01.tzt",
        "split_ticket_00.tzt",
        "split_ticket_01.tzt",
        "split_ticket_02.tzt",
        "split_ticket_03.tzt",
        "split_ticket_04.tzt",
        # NOTE: MichelsonParserError: unknown primitive `IS_IMPLICIT_ACCOUNT`
        "is_implicit_account_00.tzt",
        "is_implicit_account_01.tzt",
        # NOTE: MichelsonRuntimeError: ('SUB_MUTEZ', 'mutez', 'expected natural number, got -8')
        "sub_mutez_01.tzt",
        # NOTE: MichelsonRuntimeError: ('input', 'input', 'Stack_elt', 'unregistered primitive Lambda_rec (None args)')
        "apply_01.tzt",
        "apply_02.tzt",
        # NOTE: MichelsonRuntimeError: Expected int, got 2024-12-18T09:39:21+00:00
        "now_01.tzt",
        # NOTE: MichelsonRuntimeError: ('Stack_elt', 'Stack content is not equal to expected')
        "pack_lambda_comb_pairs.tzt",
        # NOTE: MichelsonRuntimeError: unregistered primitive Overflow (None args)
        "lsl_bytes_01.tzt",
        "lsl_nat_01.tzt",
        "lsr_nat_01.tzt",
        # NOTE: MichelsonRuntimeError: unregistered primitive Gas_exhaustion (None args)
        "gas_exhaustion.tzt",
    }

    def test_tzt(self) -> None:
        parser = MichelsonParser()
        for filename in listdir(self.path):
            if filename in self.exclude:
                continue
            with self.subTest(filename):
                filepath = join(self.path, filename)
                try:
                    with open(filepath) as file:
                        script = michelson_to_micheline(
                            file.read(),
                            parser=parser,
                        )

                        Interpreter.run_tzt(script=script)
                except Exception as e:
                    raise AssertionError(
                        f"TZT test execution failed for '{filename}'. "
                        f"This Tezos Test Format file contains Michelson code that failed during parsing or execution. "
                        f"Original error: {type(e).__name__}: {str(e)}"
                    ) from e
