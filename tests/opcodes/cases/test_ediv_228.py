from unittest import TestCase

from tests import abspath

from pytezos.repl.interpreter import Interpreter
from pytezos.michelson.converter import michelson_to_micheline
from pytezos.repl.parser import parse_expression


class OpcodeTestediv_228(TestCase):

    def setUp(self):
        self.maxDiff = None
        self.i = Interpreter(debug=True)
        
    def test_opcode_ediv_228(self):
        res = self.i.execute(f'INCLUDE "{abspath("opcodes/contracts/ediv.tz")}"')
        self.assertTrue(res['success'])
        
        res = self.i.execute('RUN (Pair -8 2) (Pair None (Pair None (Pair None None)))')
        self.assertTrue(res['success'])
        
        exp_val_expr = michelson_to_micheline('(Pair (Some (Pair -4 0)) (Pair (Some (Pair -4 0)) (Pair (Some (Pair 4 0)) (Some (Pair 4 0)))))')
        exp_val = parse_expression(exp_val_expr, res['result']['storage'].type_expr)
        self.assertEqual(exp_val, res['result']['storage']._val)
