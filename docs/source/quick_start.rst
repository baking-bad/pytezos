Quick start
=============

Introduction
------------

PyTezos library is a Python toolset for Tezos blockchain, including work with keys, signatures, contracts, operations,
RPC query builder, and a high-level interface for smart contract interaction. It can be used to build a full-fledged
application, but also it's perfect for doing researches in Jupyter interactive notebooks.
In this quick start guide, we'll go through the main concepts and inspect one of the common use cases.

Requirements
------------

Make sure you have Python 3.8+ installed and set as default in the system.

You also need to install cryptographic packages before installing the library/building the project:

*Linux*

Use apt or your favourite package manager:

.. code-block::

   $ sudo apt install libsodium-dev libgmp-dev

*MacOS*

Use homebrew:

.. code-block::

   $ brew install libsodium gmp

*Windows*

The recommended way is to use WSL and then follow the instructions for Linux,
but if you feel lucky you can try to install natively:


#. Install MinGW from `https://osdn.net/projects/mingw/ <https://osdn.net/projects/mingw/>`_
#. Make sure ``C:\MinGW\bin`` is added to your ``PATH``
#. Download the latest libsodium-X.Y.Z-msvc.zip from `https://download.libsodium.org/libsodium/releases/ <https://download.libsodium.org/libsodium/releases/>`_.
#. Extract the Win64/Release/v143/dynamic/libsodium.dll from the zip file
#. Copy libsodium.dll to C:\Windows\System32\libsodium.dll

Installation
------------

In console:

.. code-block::

   $ pip install pytezos

In Google Colab notebook:

.. code-block:: python

   >>> !apt install libsodium-dev libgmp-dev
   >>> !pip install pytezos
   [RESTART RUNTIME]

That's it! You can open Python console or Jupyter notebook and get to the next step.

Set key and RPC node
--------------------

All active interaction with the blockchain starts with the PyTezosClient:

.. code-block:: python

   >>> from pytezos import pytezos
   >>> pytezos
   <pytezos.client.PyTezosClient object at 0x7f95b0c9e5b0>

    Properties
    .key		tz1grSQDByRpnVs7sPtaprNZRp531ZKz6Jmm
    .shell		['https://rpc.tzkt.io/shadownet']
    .block_id	head

    Helpers
    .account()
    .activate_account()
    .activate_protocol()
    .bake_block()
    .balance()
    .ballot()
    .bulk()
    .check_message()
    .contract()
    .delegation()
    .double_baking_evidence()
    .double_endorsement_evidence()
    .endorsement()
    .endorsement_with_slot()
    .failing_noop()
    .now()
    .operation()
    .operation_group()
    .origination()
    .proposals()
    .register_global_constant()
    .reveal()
    .seed_nonce_revelation()
    .sign_message()
    .sleep()
    .transaction()
    .using()
    .wait()

This is one of the cool features in the interactive mode: aside from the autocomplete and call docstrings,
you can see the list of available methods for class, or list of arguments and return value for a particular methods.
We are interested in ``using`` method, which is responsible for setting up manager key and RPC connection.

.. code-block:: python

   >>> pytezos.using
   <function PyTezosClient.using at 0x7f958be02ee0>
    Change current RPC endpoint and account (private key).

    :param shell: one of 'mainnet', '***net', or RPC node uri, or instance of :class:`pytezos.rpc.shell.ShellQuery`
    :param key: base58 encoded key, path to the faucet file, faucet file itself, alias from tezos-client, or `Key`
    :param mode: whether to use `readable` or `optimized` encoding for parameters/storage/other
    :returns: A copy of current object with changes applied

Note, that by default ``pytezos`` is initialized with the latest testnet and a predefined private key for demo purpose,
so you can start to interact immediately, but it's highly recommended to use your own key. Let's do that!

Generate keys
^^^^^^^^^^^^^

.. code-block:: python

    >>> from pytezos import Key
    >>> key = Key.generate()
    >>> key
    <pytezos.crypto.key.Key object at 0x7f958bd3b7f0>

    Public key hash
    tz1N7bRGGxE6pGXS92apoybheJxNKe1jU8FB

    Helpers
    .blinded_public_key_hash()
    .from_alias()
    .from_encoded_key()
    .from_faucet()
    .from_mnemonic()
    .from_public_point()
    .from_secret_exponent()
    .generate()
    .public_key()
    .public_key_hash()
    .secret_key()
    .sign()
    .verify()

Set key as default
^^^^^^^^^^^^^^^^^^

.. code-block:: python

    >>> pytezos = pytezos.using(key=key)
    >>> pytezos
    <pytezos.client.PyTezosClient object at 0x7f958b64f190>

    Properties
    .key		tz1QeVeCHFMBd3fRj5aPxwqcAaqUDiARjwJp
    .shell		['https://rpc.tzkt.io/shadownet']
    .block_id	head

    Helpers
    .account()
    .activate_account()
    .activate_protocol()
    .bake_block()
    .balance()
    .ballot()
    .bulk()
    .check_message()
    .contract()
    .delegation()
    .double_baking_evidence()
    .double_endorsement_evidence()
    .endorsement()
    .endorsement_with_slot()
    .failing_noop()
    .now()
    .operation()
    .operation_group()
    .origination()
    .proposals()
    .register_global_constant()
    .reveal()
    .seed_nonce_revelation()
    .sign_message()
    .sleep()
    .transaction()
    .using()
    .wait()

Top up account
^^^^^^^^^^^^^^

Go to the `https://faucet.shadownet.teztnets.com/ <https://faucet.shadownet.teztnets.com/>` and paste your public key hash key file to the "Wallet address" field.
Press "Request 2001 tez" and wait for transaction to be completed.

Check that your balance is non-zero:

.. code-block:: python

   >>> pytezos.account()
   {'balance': '2001000000', 'counter': '1'}

What happened is your account has been allocated by an incoming transaction and its balance is now positive.

Reveal public key
-----------------

Now, in order to start using this key we need to send the according public key to the chain so that bakers can validate operation signatures.

.. code-block:: python

   >>> reveal_op = pytezos.reveal().send()
   >>> reveal_op
   <pytezos.operation.group.OperationGroup object at 0x7f95d73ff3d0>

    Properties
    .key		tz1QeVeCHFMBd3fRj5aPxwqcAaqUDiARjwJp
    .shell		['https://rpc.tzkt.io/shadownet']
    .block_id	head

    Hash
    oo6e7UjGkvoqXG49VRNuN5cEAjo5TqyiRJtVhTvXETbYDDahDNR

    Payload
    {'branch': 'BMCwRayudxVKJs68pAGEebhUJAtj6VRHGadkFsau8T7mbCjUXKp',
    'contents': [{'counter': '15404826',
                'fee': '370',
                'gas_limit': '1000',
                'kind': 'reveal',
                'public_key': 'edpkvHehVYEFJss7VxieJydkdbAwbSNqV9hN4SHo2P6WtsceZ24eaj',
                'source': 'tz1QeVeCHFMBd3fRj5aPxwqcAaqUDiARjwJp',
                'storage_limit': '0'}],
    'protocol': 'PtLimaPtLMwfNinJi9rCfDPWea8dFgTZ1MeJ9f1m2SRic6ayiwW',
    'signature': 'sigPcdMpWx48qsCyotSaHg3RYskNq6RWD2cJT2Nno53yUiJBpTAkGNuMnPvNc17iDqM994TNqckGm85Dxv3C6smKaKYnf7xp'}

    Helpers
    .activate_account()
    .autofill()
    .ballot()
    .binary_payload()
    .delegation()
    .double_baking_evidence()
    .double_endorsement_evidence()
    .endorsement()
    .endorsement_with_slot()
    .failing_noop()
    .fill()
    .forge()
    .hash()
    .inject()
    .json_payload()
    .message()
    .operation()
    .origination()
    .preapply()
    .proposals()
    .register_global_constant()
    .result()
    .reveal()
    .run()
    .run_operation()
    .seed_nonce_revelation()
    .send()
    .send_async()
    .sign()
    .transaction()

We can also search for operation by hash if we know exact block level or that it was injected recently:

.. code-block:: python

   >>> pytezos.shell.blocks[-20:].find_operation(reveal_op.opg_hash)
   {'protocol': 'PtLimaPtLMwfNinJi9rCfDPWea8dFgTZ1MeJ9f1m2SRic6ayiwW',
    'chain_id': 'NetXnHfVqm9iesp',
    'hash': 'oo6e7UjGkvoqXG49VRNuN5cEAjo5TqyiRJtVhTvXETbYDDahDNR',
    'branch': 'BLvDnmxUXwLMB3UyREj8ckLDdSBgzajyxZJfmoCrifZXhaRaHAL',
    'contents': [{'kind': 'reveal',
    'source': 'tz1QeVeCHFMBd3fRj5aPxwqcAaqUDiARjwJp',
    'fee': '370',
    'counter': '15404829',
    'gas_limit': '1000',
    'storage_limit': '0',
    'public_key': 'edpkvHehVYEFJss7VxieJydkdbAwbSNqV9hN4SHo2P6WtsceZ24eaj',
    'metadata': {'balance_updates': [{'kind': 'contract',
        'contract': 'tz1QeVeCHFMBd3fRj5aPxwqcAaqUDiARjwJp',
        'change': '-370',
        'origin': 'block'},
        {'kind': 'accumulator',
        'category': 'block fees',
        'change': '370',
        'origin': 'block'}],
        'operation_result': {'status': 'applied',
        'consumed_milligas': '1000000'}}}],
    'signature': 'siggMmepBSUQuavD2ws99CQtt4jRapf5HDiJM3Um26n619Y1ojCcRhxoLampysAMZZDEqVdbUXqGUXLpHzDRaTdRdCZD4p5W'}

Originate contract
------------------

Now we can do something interesting. Let's deploy a Michelson smart contract! First we need to load data, in this
tutorial we will get it from Michelson source file. There are plenty of available methods, but we'are interested in
``script`` which gives us payload for origination.

.. code-block:: python

   >>> from pytezos import ContractInterface
   >>> contract = ContractInterface.from_url('https://raw.githubusercontent.com/baking-bad/pytezos/master/tests/unit_tests/test_michelson/test_repl/mini_scenarios/ticket_wallet_fungible.tz')
   >>> contract.script
   <function ContractInterface.script at 0x7fc1768e2c10>
   Generate script for contract origination.

   :param initial_storage: Python object, leave None to generate default (attach shell/key for smart fill)
   :param mode: whether to use `readable` or `optimized` (or `legacy_optimized`) encoding for initial storage
   :return: {"code": $Micheline, "storage": $Micheline}

PyTezos can generate empty storage based on the type description, moreover it can do smart filling with the context provided (network, key).
Let's attach shell and key to the contract interface and see the default storage generated:

.. code-block:: python

    >>> ci = contract.using(key=key)
    ... ci.storage.dummy()
    {'manager': 'tz1QeVeCHFMBd3fRj5aPxwqcAaqUDiARjwJp', 'tickets': {}}

Perfect! Now we are ready to deploy the contract:

.. code-block:: python

   >>> pytezos.origination(script=ci.script()).send(min_confirmations=1)
   { ... origination operation body ... }

Note that we used synchronous injection this time, PyTezos does all the polling job for you and freezes the execution until operations is included into a block.
Previously we were searching operation using an integer offset (N levels ago), here's another example how to search an operation using branch:

.. code-block:: python

    >>> from pytezos.operation.result import OperationResult
    ... opg = pytezos.shell.blocks['BM8tcfVyd1g8yqqfE8UpasXZWFLS3Xr3cRyYaoKTTfhU9PUr1YR':] \
    ...     .find_operation('ooKx4wBV4DerrXnAEMRfZrwTyBZQQgBMGGD3xbyXeffWn88QC1f')
    ... res = OperationResult.from_operation_group(opg)
    ... res[0].originated_contracts[0]
    'KT1VtPT2CKekZnQvyR44tTNyWCKrmHdxxYBw'


Bulk injecting
----------------

The example we chose is actually a ticket wallet that can only send or receive existing tickets, so we need another contract capable of minting new ones.
Simultaneously, we will explore how to batch several operations in a single group.

.. code-block:: python

    >>> wallet = ContractInterface \
    ...     .from_url('https://raw.githubusercontent.com/baking-bad/pytezos/master/tests/unit_tests/test_michelson/test_repl/mini_scenarios/ticket_wallet_fungible.tz') \
    ...     .using(key=key)
    ...
    ... builder = ContractInterface \
    ...     .from_url('https://raw.githubusercontent.com/baking-bad/pytezos/master/tests/unit_tests/test_michelson/test_repl/mini_scenarios/ticket_builder_fungible.tz') \
    ...     .using(key=key)
    ...
    ... opg = pytezos.bulk(
    ...     wallet.originate(),
    ...     builder.originate()
    ... ).send(min_confirmations=1)
    ...
    ... [res.originated_contracts[0] for res in OperationResult.from_operation_group(opg.opg_result)]
    ['KT1S4UmLNwVcmLBE9VgHKpJJWpKE1JE8VjwN', 'KT1Si4t6ETLoj6eEsjp8hvfJeiFe3b6Z7eM5']


Call an entrypoint
-------------------

We have our contracts deployed and ready to be invoked, let's see the list of entrypoints available and their signatures:

.. code-block:: python

   >>> builder = pytezos.contract('KT1Si4t6ETLoj6eEsjp8hvfJeiFe3b6Z7eM5')
   ... builder.parameter
    <pytezos.contract.entrypoint.ContractEntrypoint object at 0x7f95d57f54c0>

    Properties
    .key		tz1QeVeCHFMBd3fRj5aPxwqcAaqUDiARjwJp
    .shell		['https://rpc.tzkt.io/shadownet']
    .address	KT1Si4t6ETLoj6eEsjp8hvfJeiFe3b6Z7eM5
    .block_id	head
    .entrypoint	default

    Builtin
    (*args, **kwargs)	# build transaction parameters (see typedef)

    Typedef
    $default:
        { "burn": ticket (unit) } ||
        { "mint": $mint }

    $mint:
        {
        "destination": contract ($destination_param),
        "amount": nat
        }

    $destination_param:
        ticket unit

    $ticket:
        /* no literal form, tickets can only be created by another contract */

    $contract:
        str  /* Base58 encoded `KT` address with optional entrypoint */ ||
        None  /* when you need to avoid type checking */ ||
        Undefined  /* `from pytezos import Undefined` for resolving None ambiguity  */

    $nat:
        int  /* Natural number */


    Helpers
    .decode()
    .encode()

And for the wallet:

.. code-block:: python

    >>> wallet = pytezos.contract('KT1S4UmLNwVcmLBE9VgHKpJJWpKE1JE8VjwN')
    >>> wallet.parameter
    <pytezos.contract.entrypoint.ContractEntrypoint object at 0x7f95d57f5fd0>

    Properties
    .key		tz1QeVeCHFMBd3fRj5aPxwqcAaqUDiARjwJp
    .shell		['https://rpc.tzkt.io/shadownet']
    .address	KT1S4UmLNwVcmLBE9VgHKpJJWpKE1JE8VjwN
    .block_id	head
    .entrypoint	default

    Builtin
    (*args, **kwargs)	# build transaction parameters (see typedef)

    Typedef
    $default:
        { "receive": ticket (unit) } ||
        { "send": $send }

    $send:
        {
        "destination": contract ($destination_param),
        "amount": nat,
        "ticketer": address
        }

    $destination_param:
        ticket unit

    $ticket:
        /* no literal form, tickets can only be created by another contract */

    $contract:
        str  /* Base58 encoded `KT` address with optional entrypoint */ ||
        None  /* when you need to avoid type checking */ ||
        Undefined  /* `from pytezos import Undefined` for resolving None ambiguity  */

    $nat:
        int  /* Natural number */

    $address:
        str  /* Base58 encoded `tz` or `KT` address */


    Helpers
    .decode()
    .encode()

Seems that we can mint a ticket using our builder and specify our wallet as a destination.
Let's also use bulk API again to demonstrate how to batch contract calls:

.. code-block:: python

    >>> opg = pytezos.bulk(
    ...    builder.mint(destination=f'{wallet.address}%receive', amount=42),
    ...    builder.mint(destination=f'{wallet.address}%receive', amount=123)
    ... ).send(min_confirmations=1)
    >>> wallet.storage['tickets'][builder.address]()
    ('KT1Si4t6ETLoj6eEsjp8hvfJeiFe3b6Z7eM5', Unit, 165)

Success!

Access storage
--------------

We have slightly touched storage access in the previous section, now let's play with `KT1REEb5VxWRjcHm5GzDMwErMmNFftsE5Gpf <https://better-call.dev/mainnet/KT1REEb5VxWRjcHm5GzDMwErMmNFftsE5Gpf/operations>`_
as it has BigMap entries, named entrypoints, and a non-trivial data scheme.

.. code-block:: python

   >>> usds = pytezos.using('mainnet').contract('KT1REEb5VxWRjcHm5GzDMwErMmNFftsE5Gpf')
   >>> usds
    <pytezos.jupyter.ContractInterface object at 0x7fc17689f2b0>

    Properties
    .key  # tz1Ne4yzDRQPd5HFz6sTaCYCNHwFubT2MWsB
    .shell  # https://mainnet-tezos.giganode.io/ (mainnet)
    .address  # KT1REEb5VxWRjcHm5GzDMwErMmNFftsE5Gpf
    .block_id  # head
    .storage  # access storage data at block `block_id`
    .parameter  # root entrypoint

    Entrypoints
    .accept_ownership()
    .burn()
    .call_FA2()
    .balance_of()
    .transfer()
    .update_operators()
    .change_master_minter()
    .change_pauser()
    .configure_minter()
    .mint()
    .pause()
    .permit()
    .remove_minter()
    .set_expiry()
    .set_transferlist()
    .transfer_ownership()
    .unpause()
    .default()

    Helpers
    .big_map_get()
    .create_from()
    .from_context()
    .from_file()
    .from_micheline()
    .from_michelson()
    .operation_result()
    .originate()
    .program()
    .script()
    .to_file()
    .to_micheline()
    .to_michelson()
    .using()

You can access contract storage at any block level, just pass block id into the ``using`` method:

.. code-block:: python

   >>> usds.using(block_id='head~10').storage()
    {'default_expiry': 300000,
     'ledger': -1,
     'metadata': -2,
     'minting_allowances': {'tz1PNsHbJRejCnnYzbsQ1CR8wUdEQqVjWen1': 999989000000,
      'tz1i2tE6hic2ASe9Kvy85ar5hGSSc58bYejT': 999985800000},
     'operators': -3,
     'paused': False,
     'permit_counter': 0,
     'permits': -4,
     'roles': {'master_minter': 'tz1i2tE6hic2ASe9Kvy85ar5hGSSc58bYejT',
      'owner': 'tz1i2tE6hic2ASe9Kvy85ar5hGSSc58bYejT',
      'pauser': 'tz1i2tE6hic2ASe9Kvy85ar5hGSSc58bYejT',
      'pending_owner': None},
     'total_supply': 20200000,
     'transferlist_contract': None}

Under the hood PyTezos has parsed the storage type, collapsed all nested structures, converted annotations into keys,
and in the result we get a simple Python object which is much easier to manipulate.
You can also access child elements by name or index (depending on the underlying Michelson type).
In order to see type definition, just remove the trailing brackets:

.. code-block:: python

   >>> usds.storage['ledger']
    <pytezos.contract.data.ContractData object at 0x7f21aaeaca30>

    Properties
    .key  # tz1Ne4yzDRQPd5HFz6sTaCYCNHwFubT2MWsB
    .shell  # https://mainnet-tezos.giganode.io/ (mainnet)
    .address  # KT1REEb5VxWRjcHm5GzDMwErMmNFftsE5Gpf
    .block_id  # head
    .path  # /ledger

    Builtin
    ()  # get as Python object
    [key]  # access child elements by name or index

    Typedef
    $ledger:
        { address: nat, … } || int /* Big_map ID */

    $address:
        str  /* Base58 encoded `tz` or `KT` address */

    $nat:
        int  /* Natural number */


    Helpers
    .decode()
    .dummy()
    .encode()
    .to_micheline()
    .to_michelson()



BigMap lookup
-------------

The approach described in the previous section also works for lazy storage, here's how you can access Big_map values:

.. code-block:: python

   >>> usds.storage['ledger']['tz1PNsHbJRejCnnYzbsQ1CR8wUdEQqVjWen1']()
   11000000

Pretty cool, hah?

View method
-------------

In the previous example we queried a token balance for a particular owner.
We can do the same using special entrypoint ``balance_of``. Let's give a look at the interface:

.. code-block:: python

   >>> usds.balance_of
    <pytezos.contract.entrypoint.ContractEntrypoint object at 0x7f4789170dc0>

    Properties
    .key  # tz1Ne4yzDRQPd5HFz6sTaCYCNHwFubT2MWsB
    .shell  # https://mainnet-tezos.giganode.io/ (mainnet)
    .address  # KT1REEb5VxWRjcHm5GzDMwErMmNFftsE5Gpf
    .block_id  # head
    .entrypoint  # balance_of

    Builtin
    (*args, **kwargs)  # build transaction parameters (see typedef)

    Typedef
    $balance_of:
        {
          "requests": [ $requests_item, … ],
          "callback": contract ($callback_param)
        }

    $callback_param:
        list (pair (pair %request (address %owner) (nat %token_id)) (nat %balance))

    $requests_item:
        {
          "owner": address,
          "token_id": nat
        }

    $address:
        str  /* Base58 encoded `tz` or `KT` address */

    $nat:
        int  /* Natural number */


    Helpers
    .decode()
    .encode()

Apparently, we need to pass a list of requests, where each item contains owner address and token ID.
In addition to that a callback address is expected which should accept the response (currently there are no on-chain views in Tezos, this async pattern is a workaround for them).
PyTezos allows you to keep that address empty and get the view result:

.. code-block:: python

   >>> usds.balance_of(requests=[
   ...   {'owner': 'tz1PNsHbJRejCnnYzbsQ1CR8wUdEQqVjWen1', 'token_id': 0},
   ...   {'owner': 'tz1i2tE6hic2ASe9Kvy85ar5hGSSc58bYejT', 'token_id': 0},
   ...   {'owner': 'tz2QegZQXyz8b74iTdaqKsGRF7YQb88Wu9CS', 'token_id': 0}
   ...], callback=None).view()
   [{'owner': 'tz1PNsHbJRejCnnYzbsQ1CR8wUdEQqVjWen1',
     'token_id': 0,
     'nat_2': 11000000},
    {'owner': 'tz1i2tE6hic2ASe9Kvy85ar5hGSSc58bYejT',
     'token_id': 0,
     'nat_2': 8200000},
    {'owner': 'tz2QegZQXyz8b74iTdaqKsGRF7YQb88Wu9CS', 'token_id': 0, 'nat_2': 0}]

Get Contract Balance
--------------------

Looking for a balance for a contract involves interacting with the contract context. You can inspect the context object to see the methods, or read about it here - :class:`pytezos.context.impl.ExecutionContext`

The context object holds general functions for retriving data about a contract/address, including the `get_balance()` call.

.. code-block:: python

   >>> kolibri_oven = pytezos.using('mainnet').contract('KT1KH3wH4sneEevPVW7AACiVKMjhTvmXLSK6')
   >>> print([x for x in dir(kolibri_oven.context) if x.startswith('get_')])
   ['get_amount', 'get_amount_expr', 'get_balance', 'get_balance_expr', 'get_big_map_diff', 'get_big_map_value', 'get_big_maps_expr', 'get_chain_id', 'get_chain_id_expr', 'get_code_expr', 'get_counter', 'get_counter_offset', 'get_dummy_address', 'get_dummy_chain_id', 'get_dummy_key_hash', 'get_dummy_lambda', 'get_dummy_public_key', 'get_dummy_signature', 'get_input_expr', 'get_level', 'get_now', 'get_now_expr', 'get_operations_ttl', 'get_originated_address', 'get_output_expr', 'get_parameter_expr', 'get_sapling_state_diff', 'get_self_address', 'get_self_expr', 'get_sender', 'get_sender_expr', 'get_source', 'get_source_expr', 'get_storage_expr', 'get_tmp_big_map_id', 'get_tmp_sapling_state_id', 'get_total_voting_power', 'get_voting_power']

   >>> kolibri_oven_balance = kolibri_oven.context.get_balance()
   >>> print("Kolibri oven {} has XTZ balance {}".format(kolibri_oven.address, kolibri_oven_balance / 1e6))
   Kolibri oven KT1KH3wH4sneEevPVW7AACiVKMjhTvmXLSK6 has XTZ balance 191.869689
