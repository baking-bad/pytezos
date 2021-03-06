from unittest import TestCase

from tests import abspath

from pytezos.repl.interpreter import Interpreter
from pytezos.michelson.converter import michelson_to_micheline
from pytezos.repl.parser import parse_expression


class OpcodeTestcompare_bytes_293(TestCase):

    def setUp(self):
        self.maxDiff = None
        self.i = Interpreter(debug=True)
        
    def test_opcode_compare_bytes_293(self):
        res = self.i.execute(f'INCLUDE "{abspath("opcodes/contracts/compare_bytes.tz")}"')
        self.assertTrue(res['success'])
        
        res = self.i.execute('RUN (Pair 0x33 0x33aa) {}')
        self.assertTrue(res['success'])
        
        exp_val_expr = michelson_to_micheline('{ False ; False ; True ; False ; True }')
        exp_val = parse_expression(exp_val_expr, res['result']['storage'].type_expr)
        self.assertEqual(exp_val, res['result']['storage']._val)
