Michelson integration tests
=============================

Basics
--------
Make sure you are familiar with the unittest package, if not - check out the docs: https://docs.python.org/3/library/unittest.html

Michelson tests are mostly based on two high-level interfaces:

- :class:`pytezos.contract.interface.ContractInterface` as a top-level entity
- :class:`pytezos.contract.call.ContractCall` for simulating contract calls
- :class:`pytezos.contract.result.ContractCallResult` for handling call results

There are also two options of executing Michelson scripts:

- :meth:`pytezos.contract.call.ContractCall.run_code` which uses standard RPC endpoint (i.e. remote Michelson interpreter)
- :meth:`pytezos.contract.call.ContractCall.interpret` that uses built-in interpreter which is not guaranteed to behave exactly as the reference one

Step by step guide
--------------------

Read this Medium article: https://medium.com/tezoscommons/testing-michelson-contracts-with-pytezos-513718499e93

Test samples
--------------

Check out test examples in this repo: https://github.com/baking-bad/pytezos/tree/master/examples

Projects using PyTezos
------------------------
See how PyTezos testing engine is used in production:

- Atomex
  https://github.com/atomex-me/atomex-michelson/blob/master/tests/test_atomex.py
- Atomex FA1.2
  https://github.com/atomex-me/atomex-fa12-ligo/tree/master/tests
- TQTezos MAC
  https://github.com/tqtezos/smart-contracts/tree/master/multi_asset/tezos_mac_tests
- Equisafe NYX
  https://gitlab.com/equisafe/nyx/-/tree/master/tests