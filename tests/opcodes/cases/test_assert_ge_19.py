from unittest import TestCase

from tests import abspath

from pytezos.repl.interpreter import Interpreter
from pytezos.michelson.converter import michelson_to_micheline
from pytezos.repl.parser import parse_expression


class OpcodeTestassert_ge_19(TestCase):

    def setUp(self):
        self.maxDiff = None
        self.i = Interpreter(debug=False)  # disable exceptions

    def test_opcode_assert_ge_19(self):
        res = self.i.execute(f'INCLUDE "{abspath("opcodes/contracts/assert_ge.tz")}"')
        self.assertTrue(res['success'])

        res = self.i.execute('RUN (Pair -1 0) Unit')
        self.assertEqual(False, res['success'])
