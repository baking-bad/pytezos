# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

PyTezos — Python toolkit for the Tezos blockchain. Ships two packages from `src/`:

- `pytezos` — SDK: RPC client, crypto, operation forging, contract interaction, Michelson parser/interpreter, sandbox runner.
- `michelson_kernel` — Jupyter kernel that wraps the Michelson interpreter.

Two console scripts are installed (see `pyproject.toml`):

- `pytezos` → `pytezos.cli.cli:cli`
- `michelson-kernel` → `michelson_kernel.cli:cli`

Requires Python 3.10–3.13 and native libs `libsodium`, `gmp`, `pkg-config` (see README for per-OS install). Dependencies are managed with uv (PEP 621 `[project]` + PEP 735 `[dependency-groups]`); `uv.lock` is committed.

## Common commands

All workflow commands live in the `Makefile` (run `make help` for the full list). Highlights:

- `make install` — `uv sync --all-extras --all-groups --link-mode symlink --locked`. To install without dev deps: `uv sync --no-default-groups --locked`.
- `make install-deps` — install native deps (`libsodium`, `gmp`, `pkg-config`) for the current OS.
- `make lint` — runs `isort`, `black`, `ruff`, and `mypy` against `src/`, `tests/`, `scripts/`. Each is also a standalone target (`make ruff`, `make mypy`, etc.). Line length is 120; `black` uses single quotes (`skip-string-normalization`), `isort` uses `force_single_line`.
- `make test` — full local suite. Runs contract/integration/unit tests in parallel with `pytest-xdist`, then `tests/sandbox_tests` serially (sandbox tests require Docker and start real Octez nodes via `testcontainers`).
- `make test-ci` — emits JUnit XML per suite; sandbox suite only on Linux.
- `make docs` — builds Sphinx docs; depends on `make kernel-docs rpc-docs`. `rpc-docs` calls `scripts/fetch_rpc_docs.py` and needs `DOCS_RPC_URL` pointed at a full node.
- `make image` — builds `pytezos.dockerfile` and `michelson-kernel.dockerfile`.
- `make update` — `uv sync -U --all-extras --all-groups` to bump deps and refresh `uv.lock`. The `notebook` dependency lives in the `jupyter` extra; the `michelson-kernel` Docker image installs it via `--extra jupyter`, the headless `pytezos` image does not.

Run a single test via uv directly, e.g.:

```
uv run pytest -xvs tests/unit_tests/test_michelson/test_parse.py::TestParse::test_some_case
```

Sandbox tests must not be parallelized (they bind ports) — call `pytest -xv tests/sandbox_tests/...` per `make test`.

## Test layout

- `tests/unit_tests/` — pure Python, fastest tier; no network, no Docker.
- `tests/contract_tests/` — generated from on-chain contracts. Regenerate with `make update-contracts` (`scripts/fetch_contract_data.py` then `scripts/generate_contract_tests.py`).
- `tests/integration_tests/` — talk to remote RPC endpoints.
- `tests/sandbox_tests/` — spin up dockerized Octez nodes via `pytezos.sandbox.node`. Linux-only in CI.

## Architecture

### Client entry point

`pytezos/__init__.py` exposes `pytezos = PyTezosClient()` — the canonical entry point. `PyTezosClient` (in `pytezos/client.py`) composes `ContextMixin` + `ContentMixin`; nearly every higher-level object (operations, contract interfaces, shell queries) is created via `self._spawn_context()`, which threads an `ExecutionContext` (`pytezos/context/impl.py`) through the call chain. When changing client behavior, look at the context layer first — it's the shared state for keys, RPC shell, block hash, chain id, etc.

### Layered modules (in `src/pytezos/`)

- `crypto/` — `Key` (ed25519/secp256k1/p256), signing, mnemonic derivation. Uses `pysodium`, `coincurve`, `fastecdsa`.
- `rpc/` — HTTP client (`shell.py`, `node.py`), typed query tree (`query.py`), error mapping (`errors.py`). `ShellQuery` is the dynamic facade returned by `pytezos.shell`.
- `operation/` — building, forging, signing, injecting operations. Forging logic in `pytezos/michelson/forge.py` is shared with Michelson.
- `michelson/` — Michelson tooling:
  - `parse.py` / `format.py` — text ↔ Micheline JSON.
  - `forge.py` — binary forge / unforge (used for both ops and Micheline values).
  - `types/` — runtime type system (`int`, `pair`, `map`, `big_map`, `ticket`, `sapling`, `bls`, etc.).
  - `instructions/` — each Michelson opcode group; called by `program.py` to walk the stack.
  - `sections/` — `parameter`/`storage`/`code`/`view`/`tzt` top-level sections.
  - `repl.py` — `Interpreter`, the Python reimplementation of the Michelson VM; this is what powers the Jupyter kernel and local contract simulation.
  - `program.py`, `stack.py`, `micheline.py` — execution model and AST glue.
- `contract/` — high-level smart-contract surface: `ContractInterface` (loaded from on-chain address, file, or Michelson source), `ContractCall`, `entrypoint.py`, `view.py`, TZIP-16 metadata.
- `block/`, `protocol/` — block header utilities and protocol diff/upgrade helpers.
- `sandbox/` — `node.SandboxedNodeTestCase` and friends launch Octez via Docker (`testcontainers`); per-protocol parameter JSON lives alongside as `<NNN-protohash>-parameters/`. `parameters.py` holds the protocol-hash constants and selects `LATEST`.
- `cli/` — Click-based `pytezos` CLI (codegen, deploy, sandbox, GitHub integration in `github.py`).

### Michelson kernel (`src/michelson_kernel/`)

Jupyter kernel that wraps `michelson.repl.Interpreter`. `cli.py` provides `michelson-kernel install/run`. Generated reference docs come from `scripts/generate_kernel_docs.py` (writes into `docs.py`) — do not edit `docs.py` by hand; `black` skips it via `--exclude ".*/docs.py"`.

## Adding support for a new protocol

(Condensed from `CONTRIBUTING.md` — read that for the full sandboxed-node flow.)

1. Bump `pytezos.sandbox.node.DOCKER_IMAGE` to the new Octez image tag.
2. Add the new protocol hash constant in `pytezos/sandbox/parameters.py`, append it to `protocol_hashes` / `protocol_version`, and set `LATEST`.
3. Drop the new sandbox `parameters` JSON into `src/pytezos/sandbox/<NNN-protohash>-parameters/` (the `sandbox-params` Makefile target copies these out of the official `tezos/tezos:master` image — note that target uses a hardcoded `024-PtTALLiN-parameters` path you'll need to update).
4. Refresh RPC docs (`DOCS_RPC_URL=... make rpc-docs`) and read the protocol release notes for code changes.
5. Verify with `make all` plus a manual `pytezos sandbox` / `michelson-kernel run`.

## Release flow

1. Branch `aux/X.Y.Z`, update `version` in `pyproject.toml`.
2. `make before_release` (= `make update all` — refreshes deps, lints, tests, docs).
3. Update `CHANGELOG.md` in the existing format.
4. Merge to `master`, tag `X.Y.Z`, push tag.
