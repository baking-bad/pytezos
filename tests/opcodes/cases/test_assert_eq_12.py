from unittest import TestCase

from tests import abspath

from pytezos.michelson.interpreter.repl import Interpreter


class OpcodeTestassert_eq_12(TestCase):

    def setUp(self):
        self.maxDiff = None
        self.i = Interpreter(debug=False)  # disable exceptions

    def test_opcode_assert_eq_12(self):
        res = self.i.execute(f'INCLUDE "{abspath("opcodes/contracts/assert_eq.tz")}"')
        self.assertTrue(res['success'])

        res = self.i.execute('RUN (Pair 0 -1) Unit')
        self.assertEqual(False, res['success'])
