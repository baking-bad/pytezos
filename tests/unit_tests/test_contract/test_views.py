from os.path import join, dirname
from pytezos import ContractInterface, MichelsonRuntimeError
from unittest import TestCase


class ViewsTest(TestCase):

    def test_onchain_view(self):
        ci = ContractInterface.from_file(join(dirname(__file__), 'contracts', 'view_toplevel_lib.tz'))

        with self.assertRaises(MichelsonRuntimeError):
            ci.test_failwith(0).onchain_view()

        res = ci.add(2).onchain_view(storage=1)
        self.assertEqual(3, res)

        res = ci.fib(10).onchain_view(storage=0)
        self.assertEqual(55, res)