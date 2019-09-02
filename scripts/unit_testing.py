from unittest import TestCase

from pytezos import ContractInterface, Contract

code = """
parameter bytes;
storage (pair :storage (big_map bytes timestamp) nat);
code { DUP ;
       DIP { CDR @storage_slash_1 } ;
       CAR @hash_slash_2 ;
       PUSH nat 1 ;
       { DIP { { DIP { DUP @storage } ; SWAP } } ; SWAP } ;
       CDR %counter ;
       ADD @counter ;
       { DIP { { DIP { DUP @storage } ; SWAP } } ; SWAP } ;
       CAR %records ;
       NOW ;
       { DIP { { DIP { { DIP { DUP @hash } ; SWAP } } ; SWAP } } ; SWAP } ;
       DIP { SOME } ;
       DIP { DIP { DIP { DIP { DROP ; DROP } } } } ;
       UPDATE @records ;
       PAIR %records %counter ;
       NIL operation ;
       PAIR }
"""


class SampleContractTest(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.ci = ContractInterface(contract=Contract.from_michelson(code))
        print(cls.ci.contract.parameter)
        print(cls.ci.contract.storage)
        print(cls.ci)

    def test_invocation(self):
        res = self.ci.call('deadbeef').result(storage=self.ci.contract.storage.default())
        self.assertEqual(1, res.storage[1])
        self.assertIn('deadbeef', res.big_map_diff)