# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog], and this project adheres to [Semantic Versioning].

## [3.17.0](https://github.com/baking-bad/pytezos/compare/3.16.1...3.17.0) - 2026-01-19

### Added

- Tallinn protocol support (024).
- `IS_IMPLICIT_ACCOUNT` Michelson instruction.

### Fixed

- Proof field forging for reveal operations.

### Changed

- Octez binaries updated to v24.0
- Removed `adaptive_issuance_vote` from block headers (no longer in Tallinn).

## [3.16.1](https://github.com/baking-bad/pytezos/compare/3.16.0...3.16.1) - 2026-10-27

### Fixed

- Michelson TZT tests updated and moved to new repo
- Other maintenance infrastacture fixes

## [3.16.0](https://github.com/baking-bad/pytezos/compare/3.15.0...3.16.0) - 2026-09-15

### Added

- Seoulnet protocol support.

### Changed

- Octez binaries updated to v23.2

## [3.15.0](https://github.com/baking-bad/pytezos/compare/3.14.0...3.15.0) - 2025-04-11

### Added

- Rionet protocol support.

### Changed

- Octez binaries updated to v22.0-1

## [3.14.0](https://github.com/baking-bad/pytezos/compare/3.13.6...3.14.0) - 2025-01-18

### Added

- Quebecnet protocol support.
- Python 3.13 support.

### Changed

- Octez binaries updated to v21.2-1

### Fixed

- Fixed Python 3.9 compatibility

### Removed

- Removed Python 3.8 support.

## [3.13.6](https://github.com/baking-bad/pytezos/compare/3.13.5...3.13.6) (2024-12-13)

### Fixed

- Fixed `tz4` signing suite.

### Changed

- Octez binaries updated to v21.0-1

## [3.13.5](https://github.com/baking-bad/pytezos/compare/3.13.4...3.13.5) (2024-10-28)

### Added

- Added `tz4` address support.

### Changed

- Octez binaries updated to v20.3-1

## [3.13.4](https://github.com/baking-bad/pytezos/compare/3.13.3...3.13.4) - 2024-08-19

### Fixed

- Fixed testcontainers version constraint.

## [3.13.3](https://github.com/baking-bad/pytezos/compare/3.13.2...3.13.3) - 2024-07-12

### Fixed

- Fixed Python 3.12 compatibility on .deb-based systems.

### Changed

- `secp256k1` dependency replaced with `coincurve`.

## [3.13.2](https://github.com/baking-bad/pytezos/compare/3.13.1...3.13.2) - 2024-06-27

### Fixed

- Fixed Parisnet operation injections.

## [3.13.1](https://github.com/baking-bad/pytezos/compare/3.13.0...3.13.1) - 2024-06-24

### Fixed

- Fixed Google Colab installation

## [3.13.0](https://github.com/baking-bad/pytezos/compare/3.12.1...3.13.0) - 2024-06-24

### Added

- ParisCnet protocol support.

### Changed

- Octez binaries updated to v20.1-1

### Fixed

- Fixed Python 3.8 compatibility

## [3.12.1](https://github.com/baking-bad/pytezos/compare/3.12.0...3.12.1) - 2024-06-11

### Changed

- Octez binaries updated to v20.0-3

## [3.12.0](https://github.com/baking-bad/pytezos/compare/3.11.3...3.12.0) - 2024-05-27

### Added

- Parisnet protocol support
- Compatibility with Python 3.12

### Changed

- Octez binaries updated to v20.0-rc1

## [3.11.3](https://github.com/baking-bad/pytezos/compare/3.11.2...3.11.3) - 2024-02-23

### Fixed

- Updated cryptographic libraries

## [3.11.2](https://github.com/baking-bad/pytezos/compare/3.11.1...3.11.2) - 2024-02-22

### Fixed

- Fixed protocol parameters for sandboxed node

## [3.11.1](https://github.com/baking-bad/pytezos/compare/3.11.0...3.11.1) - 2024-02-07

### Added

- Forging/encoding for Smart Rollup State hash

## [3.11.0](https://github.com/baking-bad/pytezos/compare/3.10.3...3.11.0) - 2024-02-05

### Added

- Compatibility with Oxfordnet protocol
- Octez binaries updated to v19.0

## [3.10.3](https://github.com/baking-bad/pytezos/compare/3.10.2...3.10.3) - 2023-11-27

### Fixed

- Smart rollup address validation

## [3.10.2](https://github.com/baking-bad/pytezos/compare/3.10.1...3.10.2) - 2023-07-05

### Fixed

- Missing validation pass info for sr operation kinds


## [3.10.1](https://github.com/baking-bad/pytezos/compare/3.10.0...3.10.1) - 2023-07-04

### Added

- Sending/forging new operation kinds: `transfer_ticket`, `smart_rollup_add_messages`, and `smart_rollup_execute_outbox_message`

## [3.10.0](https://github.com/baking-bad/pytezos/compare/3.9.0...3.10.0) - 2023-06-13

### Added

- Compatibility with Nairobi protocol

## [3.9.0](https://github.com/baking-bad/pytezos/compare/3.8.0...3.9.0) - 2023-03-29

### Fixed

- Quickstart tutorial

### Added

- `NAT`, `BYTES` opcodes support
- Minimal support for `tz4` and `sr1` addresses

### Changed

- `INT` opcode semantics changed
- Block time and dependent variables are changed according to the proto
- Sandbox node binaries updated to v16

## [3.8.0](https://github.com/baking-bad/pytezos/compare/3.7.4...3.8.0) - 2023-02-21

### Fixed

- Conflicting `bson` module is replaced by an alternative

### Added

- Compatibility with Python 3.11

### Changed

- Docker images are significantly smaller (231MB -> 107MB for `pytezos`, 834MB -> 234MB for `michelson-kernel`

## [3.7.4](https://github.com/baking-bad/pytezos/compare/3.7.3...3.7.4) - 2023-01-12

### Fixed

- `TICKET` binary tag and semantics was changed in accordance with Lima

### Added

- `LAMBDA_REC` instruction support
- Optional custom headers for node RPC requests

## [3.7.3](https://github.com/baking-bad/pytezos/compare/3.7.2...3.7.3) - 2022-12-20

### Fixed

- Added new reserved entrypoint `deposit` which changes the way forging works
- Update test container version
- Fixed error message formatting in `wait_operations` helper (@owen9825

## [3.7.2](https://github.com/baking-bad/pytezos/compare/3.7.1...3.7.2) - 2022-11-22

### Added

- `ContractView.run_view` helper that allows to execute on-chain view via special RPC endpoint

## [3.7.1](https://github.com/baking-bad/pytezos/compare/3.7.0...3.7.1) - 2022-10-15

### Fixed

- Fixed lazy storage diff parsing in `OperationResult` helper class
- `UNPAIR n` is now actually counting leaves (by @konchunas

## [3.7.0](https://github.com/baking-bad/pytezos/compare/3.6.1...3.7.0) - 2022-09-17

### Added

- `EMIT` instruction support added

### Changed

- `consumed_milligas` is used instead of deprecated `consumed_gas` field
- `ghostnet` is now a default network in pytezos client (as it is permanent

## [3.6.1](https://github.com/baking-bad/pytezos/compare/3.6.0...3.6.1) - 2022-08-04

### Added

- one can supply initial storage when executing a callback view

### Fixed

- Fixed PLY & -OO mode incompatibility
- Fixed `pytezos sandbox` command crash.
- Fixed setting default logging config.
- Large batches do not hit gas per block exhausted anymore, fee is specified for the first operation only.

## [3.6.0](https://github.com/baking-bad/pytezos/compare/3.5.1...3.6.0) - 2022-06-28

### Added

- Added Jakarta primitives support: `tx_rollup_l2_address`, `MIN_BLOCK_TIME`, `sapling_transaction_deprecated`.

### Fixed

- Fixed `gas_exhausted.block` error when sending multiple operations in a single batch.

### Deprecated

- Protocols older than 13.0 (Jakatra) are no longer supported.

## [3.5.1](https://github.com/baking-bad/pytezos/compare/3.5.0...3.5.1) - 2022-05-18

### Fixed

- Unforging for `pair` with 3 args and annots was working incorrectly (@konchunas

## [3.5.0](https://github.com/baking-bad/pytezos/compare/3.4.2...3.5.0) - 2022-04-29

### Fixed

- Wait helper edge case: operations can be both included in chain and present in mempool
- Batch operation build was accompanied by many useless RPC requests
- `minimal_block_delay` constant might be absent, defaults to 0 (by @jpic

### Changed

- Minimum Python version is now 3.8, Python 3.10 support is added
- Blocks observer now handles reorgs and waits for N levels instead of N blocks

## 3.4.2 - 2022-03-26

### Fixed`

- time_between_blocks no longer exists, minimum_block_delay used instead
- sandbox tests -> re-create node container per each case (cannot rollback in Tenderbake
- REPL: `CREATE_CONTRACT` is now able to originate contracts with views (by @konchunas

### Added

- `SUB_MUTEZ` instruction support in REPL
- Implementations of `Operation_list_hash`, `Operation_list_list_hash`, and `Block_payload_hash`

## 3.4.1 - 2022-03-22

### Fixed

- Issue with `lazy_storage_diff`

## 3.4.0 - 2022-03-22

### Fixed

- `run_code` does not merge lazy storage diffs correctly

### Changed

- Default protocol is Ithaca
- Sandbox node version is updated to v12

## 3.3.6 - 2022-03-10

### Fixed

- Logging configuration is not overwritten by pytezos

### Added

- Installation hints for M1 (credits to @konchunas

## 3.3.5 - 2022-02-28

### Fixed

- Metadata big map can be located in a nested structure, not necessarily on the top-level (as per TZIP-16

## 3.3.4 - 2021-12-23

### Fixed

- New testnet faucet is handled properly (the json format has slightly changed
- Incorrect wrapping of static methods while injecting jupyter docs (py3.10
- Unable to call intermediate entrypoints from the contract interfaceE
- Sandboxed node wasn't exposed at localhost causing connection issues on MacOS and Windows
- Big map key of nested or/pair type wasn't handled correctly

### Changed

- `Key.verify` returns `True` if the signature is valid (it was `None` before

## 3.3.3 - 2021-12-14

### Fixed

- Always try to fetch the latest storage in off-chain or on-chain views
- Fixed case with `GET` instruction returning `None` with wrong type (key type instead of value type

## 3.3.2 - 2021-12-12

### Added

- explicit handling of the 401 to return a more meaningful response [@kaellis]

### Fixed

- Regression in offline view behavior for storage with bigmaps

## 3.3.1 - 2021-12-01

### Added

- Ability to patch VIEW results when using `interpret()` or `onchain_view()`

### Fixed

- Results returned from the callback views are now fully-annotated (based on the callback contract type

## 3.3.0 - 2021-11-26

### Added

- Changelog 😅
- Support for on-chain views:
  - Multiple `view` sections are correctly parsed/unparsed
  - in REPL `VIEW` instruction works both with self-recursive calls and on-chain contracts (if shell is attached
  - `ContractInterface` provides a seamless interface to views (works pretty much the same as with off-chain views
- Partial support for global constants:
  - added new operation kind `register_global_constant`
  - `ExecutionContext` allows to register constants as well
  - `ContractInterface` resolves all the constants using the context upon creation
  - Since there is no RPC for retrieving on-chain global constants proper resolving cannot be implemented
  - It is not possible to use constants in transaction parameters and origination script with high-level entities
- Minimal support for timelock feature:
  - `chest`, `chest_key`, and `CHEST` primitives are supported in parser, but not in the REPL
  - There are currenty no way to construct a timelock

### Changed

- Hangzhou (PtHangz2) RPC endpoint (`hangzhou` is the default shell now), sandbox image (`v11.0-1`

### Fixed

- `pytezos sandbox` CLI command now works properly and provides almost flextesa-like experience at lesser cost
- Operation branch was calculated incorrectly based on the TTL (before `head~{60-ttl}`, after `head~{120-ttl}`

<!-- Links -->
[keep a changelog]: https://keepachangelog.com/en/1.0.0/
[semantic versioning]: https://semver.org/spec/v2.0.0.html

<!-- Versions -->
