High-level interfaces
================================

PyTezos client
++++++++++++++++
.. autoclass:: pytezos.client.PyTezosClient
   :members:
   :inherited-members:

Contract interface
++++++++++++++++++++
.. autoclass:: pytezos.contract.interface.ContractInterface
   :members:
   :inherited-members:

Entrypoint / view namespace
+++++++++++++++++++++++++++
.. autoclass:: pytezos.contract.interface.ContractProxyNamespace
   :members:

Contract entrypoint proxy
+++++++++++++++++++++++++++
.. autoclass:: pytezos.contract.entrypoint.ContractEntrypoint
   :members:
   :special-members: __call__
   :inherited-members:

Contract call proxy
+++++++++++++++++++++
.. autoclass:: pytezos.contract.call.ContractCall
   :members:
   :inherited-members:

Contract call result
++++++++++++++++++++++
.. autoclass:: pytezos.contract.result.ContractCallResult
   :members:

Contract storage proxy
++++++++++++++++++++++
.. autoclass:: pytezos.contract.data.ContractData
   :members:
   :special-members: __call__
   :inherited-members:

Contract view proxy
+++++++++++++++++++
.. autoclass:: pytezos.contract.view.ContractView
   :members:
   :inherited-members:
