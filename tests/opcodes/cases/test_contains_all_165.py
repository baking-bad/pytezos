from unittest import TestCase

from tests import abspath

from pytezos.repl.interpreter import Interpreter
from pytezos.michelson.converter import michelson_to_micheline
from pytezos.repl.parser import parse_expression


class OpcodeTestcontains_all_165(TestCase):

    def setUp(self):
        self.maxDiff = None
        self.i = Interpreter(debug=True)
        
    def test_opcode_contains_all_165(self):
        res = self.i.execute(f'INCLUDE "{abspath("opcodes/contracts/contains_all.tz")}"')
        self.assertTrue(res['success'])
        
        res = self.i.execute('RUN (Pair { "B" ; "B" ; "asdf" ; "C" } { "B" ; "C" ; "asdf" }) None')
        self.assertTrue(res['success'])
        
        exp_val_expr = michelson_to_micheline('(Some True)')
        exp_val = parse_expression(exp_val_expr, res['result']['storage'].type_expr)
        self.assertEqual(exp_val, res['result']['storage']._val)
