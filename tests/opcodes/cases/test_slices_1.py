from unittest import TestCase

from tests import abspath

from pytezos.repl.interpreter import Interpreter
from pytezos.michelson.converter import michelson_to_micheline
from pytezos.repl.parser import parse_expression


class OpcodeTestslices_1(TestCase):

    def setUp(self):
        self.maxDiff = None
        self.i = Interpreter(debug=False)  # disable exceptions

    def test_opcode_slices_1(self):
        res = self.i.execute(f'INCLUDE "{abspath("opcodes/contracts/slices.tz")}"')
        self.assertTrue(res['success'])

        res = self.i.execute('RUN (Pair 0xeaa9ab79e8b84ef0e55c43a9a857214d8761e67b75ba63500a5694fb2ffe174acc2de22d01ccb7259342437f05e1987949f0ad82e9f32e9a0b79cb252d7f7b8236ad728893f4e7150742eefdbeda254970f9fcd92c6228c178e1a923e5600758eb83f2a05edd0be7625657901f2ba81eaf145d003dbef78e33f43a32a3788bdf0501000000085341554349535345 "spsig1PPUFZucuAQybs5wsqsNQ68QNgFaBnVKMFaoZZfi1BtNnuCAWnmL9wVy5HfHkR6AeodjVGxpBVVSYcJKyMURn6K1yknYLm") "sppk7dBPqMPjDjXgKbb5f7V3PuKUrA4Zuwc3c3H7XqQerqPUWbK7Hna"')
        self.assertEqual(False, res['success'])
