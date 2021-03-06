from unittest import TestCase

from tests import abspath

from pytezos.repl.interpreter import Interpreter
from pytezos.michelson.converter import michelson_to_micheline
from pytezos.repl.parser import parse_expression


class OpcodeTestassert_neq_13(TestCase):

    def setUp(self):
        self.maxDiff = None
        self.i = Interpreter(debug=False)  # disable exceptions

    def test_opcode_assert_neq_13(self):
        res = self.i.execute(f'INCLUDE "{abspath("opcodes/contracts/assert_neq.tz")}"')
        self.assertTrue(res['success'])

        res = self.i.execute('RUN (Pair -1 -1) Unit')
        self.assertEqual(False, res['success'])
