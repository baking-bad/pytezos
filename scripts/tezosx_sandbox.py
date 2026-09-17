# /// script
# requires-python = ">=3.10"
# dependencies = ["requests"]
# ///
"""Local Tezos X Michelson sequencer for integration tests, no L1 and no rollup node.

The Tezos X Michelson L2 ("Tezlink" runtime inside `octez-evm-node`) speaks the Tezos node
RPC but has no mempool and runs its own fee policy. `octez-evm-node run sandbox` boots the
same binary and kernel that serve the public previewnet, so a container on this machine
reproduces the RPC surface pytezos has to cope with (`/mempool/pending_operations` 404,
`/mempool/filter` with previewnet thresholds, 1s blocks).

Three things stand between the stock image and a running sandbox, all handled here:

1. The previewnet kernel is an *installer* that reveals ~2200 content-addressed preimages.
   The node fetches them one HTTPS request at a time (~30 min); `prepare` walks the tree in
   parallel and hands the files over via `--preimages-dir`.
2. `--network previewnet` makes the node compare the sandbox's zero rollup address with the
   real one and abort. The installer is therefore passed explicitly with `--kernel`.
3. The installer bakes in previewnet's sequencer public key; the sandbox can't sign with it.
   `prepare` swaps that preimage for a throwaway key of ours (same-length hash, so nothing
   else in the wasm moves) and `run` signs blocks with it.

Usage:

    uv run scripts/tezosx_sandbox.py prepare          # once; ~1 min, cached under --dir
    uv run scripts/tezosx_sandbox.py run              # boots, funds alice, waits for level 140
    TEZOSX_RPC_URL=http://localhost:8545/tezlink TEZOSX_SECRET_KEY=<alice edsk> \\
        uv run pytest tests/integration_tests/test_tezosx.py
    uv run scripts/tezosx_sandbox.py stop

The chain must be older than 115 blocks before pytezos can branch an operation on
`head~(120-ttl)`, hence the wait in `run`.
"""

import argparse
import hashlib
import json
import re
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import requests

# Same commit as https://michelson.previewnet.tezosx.nomadic-labs.com/version (2026-09-04)
IMAGE = 'tezos/tezos:octez-evm-node-v0.65_0ee84d6b_20260824173257'
COMMIT = '0ee84d6bf5fe976c5a657ce3be092ce256d035d8'
INSTALLER_URL = (
    'https://gitlab.com/api/v4/projects/tezos%2Ftezos/repository/files/'
    f'etherlink%2Fbin_node%2Finstallers%2Fpreviewnet-installer.wasm/raw?ref={COMMIT}'
)
PREIMAGES_ENDPOINT = 'https://relay.previewnet.tezosx.nomadic-labs.com/wasm_2_0_0'
CONTAINER = 'tezosx-sandbox'

# Throwaway sandbox sequencer key (secp256r1); any key works, it only signs local blocks.
SEQUENCER_SK = 'p2sk3SmiEdmLuq9urez2hnoD24aEfQ1gvCgvzvz9gMZYAPBvDnNMUQ'
SEQUENCER_PK = 'p2pk66qSs89GBZXKh1WUznL5pmqnkEL4pkeYdY7WA1PzWuSt9u5m2qA'

# pytezos `alice` (src/pytezos/context/mixin.py)
ALICE_PKH = 'tz1VSUr8wwNhLAzempoch5d6hLRiTh8Cjcjb'

DEFAULT_DIR = Path.home() / '.cache' / 'pytezos' / 'tezosx-sandbox'


# --- prepare -----------------------------------------------------------------------------


def page_children(page: bytes) -> list:
    """A preimage page is `tag(1) | len(4 BE) | payload`; tag 1 pages list 33-byte child hashes."""
    if page[0] != 1:
        return []
    size = int.from_bytes(page[1:5], 'big')
    body = page[5 : 5 + size]
    return [body[i : i + 33].hex() for i in range(0, len(body), 33)]


def fetch_preimages(roots: list, out: Path) -> int:
    out.mkdir(parents=True, exist_ok=True)
    session = requests.Session()

    def fetch(h: str) -> bytes:
        path = out / h
        if path.exists():
            return path.read_bytes()
        res = session.get(f'{PREIMAGES_ENDPOINT}/{h}', timeout=30)
        res.raise_for_status()
        path.write_bytes(res.content)
        return res.content

    frontier, total = list(roots), 0
    with ThreadPoolExecutor(max_workers=32) as pool:
        while frontier:
            pages = list(pool.map(fetch, frontier))
            total += len(frontier)
            frontier = [child for page in pages for child in page_children(page)]
    return total


def reveal_hashes(installer: bytes) -> list:
    """Every hash the installer reveals: the kernel's root plus one per config value
    (each serialized as `21 000000 <33-byte hash>`)."""
    return [m.group(1).hex() for m in re.finditer(rb'\x21\x00\x00\x00(\x00.{32})', installer, re.DOTALL)]


def find_reveal_hash(installer: bytes, path: bytes) -> bytes:
    needle = bytes([len(path)]) + path
    i = installer.find(needle)
    assert i > 0, f'{path!r} not found in installer'
    j = i - 33
    assert installer[j - 8 : j] == bytes.fromhex('0000000021000000'), installer[j - 8 : j].hex()
    return installer[j : j + 33]


def content_page(payload: bytes) -> bytes:
    return b'\x00' + len(payload).to_bytes(4, 'big') + payload


def page_hash(page: bytes) -> bytes:
    return b'\x00' + hashlib.blake2b(page, digest_size=32).digest()


def patch_sequencer(installer: bytes, preimages: Path, public_key: str) -> bytes:
    old_hash = find_reveal_hash(installer, b'/evm/world_state/sequencer')
    old_page = (preimages / old_hash.hex()).read_bytes()
    assert page_hash(old_page) == old_hash, 'preimage hashing scheme mismatch'
    print('installer sequencer key:', old_page[5:].decode(), '->', public_key)
    page = content_page(public_key.encode())
    (preimages / page_hash(page).hex()).write_bytes(page)
    return installer.replace(old_hash, page_hash(page))


def prepare(base: Path) -> None:
    kernel_dir, preimages = base / 'kernel', base / 'preimages'
    kernel_dir.mkdir(parents=True, exist_ok=True)
    installer_path = kernel_dir / 'previewnet-installer.wasm'
    if not installer_path.exists():
        res = requests.get(INSTALLER_URL, timeout=120)
        res.raise_for_status()
        installer_path.write_bytes(res.content)
    installer = installer_path.read_bytes()
    roots = reveal_hashes(installer)
    print(f'fetching preimage trees of {len(roots)} reveals')
    print('preimages:', fetch_preimages(roots, preimages))
    (kernel_dir / 'sandbox-installer.wasm').write_bytes(patch_sequencer(installer, preimages, SEQUENCER_PK))
    print('ready:', base)


# --- run / stop ----------------------------------------------------------------------------


def rpc_url(port: int) -> str:
    return f'http://localhost:{port}/tezlink'


def head_level(url: str) -> int:
    try:
        return int(requests.get(f'{url}/chains/main/blocks/head/header', timeout=3).json()['level'])
    except Exception:  # noqa: BLE001
        return -1


def run(base: Path, port: int, fund: list, min_level: int, block_delay: float) -> None:
    subprocess.run(['docker', 'rm', '-f', CONTAINER], capture_output=True, check=False)
    cmd = [
        'docker', 'run', '-d', '--name', CONTAINER, '-p', f'{port}:8545',
        '-v', f'{base / "kernel"}:/kernel:ro', '-v', f'{base / "preimages"}:/preimages',
        '--entrypoint', 'octez-evm-node', IMAGE,
        'run', 'sandbox', '--data-dir', '/tmp/tezosx', '--with-runtime', 'tezos',
        '--kernel', '/kernel/sandbox-installer.wasm', '--preimages-dir', '/preimages',
        '--preimages-endpoint', PREIMAGES_ENDPOINT,
        '--sequencer-key', f'unencrypted:{SEQUENCER_SK}',
        '--rpc-addr', '0.0.0.0', '--rpc-port', '8545', '--time-between-blocks', str(block_delay),
    ]  # fmt: skip
    for pkh in fund:
        cmd += ['--fund', pkh]
    subprocess.run(cmd, check=True, capture_output=True)
    url = rpc_url(port)
    started = time.time()
    while head_level(url) < min_level:
        running = subprocess.run(
            ['docker', 'inspect', '-f', '{{.State.Running}}', CONTAINER], capture_output=True, text=True
        )
        if running.stdout.strip() != 'true':
            logs = subprocess.run(['docker', 'logs', '--tail', '20', CONTAINER], capture_output=True, text=True)
            sys.exit(f'{CONTAINER} died:\n{logs.stdout}{logs.stderr}')
        if time.time() - started > 600:
            sys.exit(f'{CONTAINER} did not reach level {min_level} in 10 min')
        time.sleep(2)
    print(
        json.dumps({'rpc': url, 'level': head_level(url), 'funded': fund, 'boot_seconds': round(time.time() - started)})
    )


def stop() -> None:
    subprocess.run(['docker', 'rm', '-f', CONTAINER], capture_output=True, check=False)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.split('\n\n')[0])
    parser.add_argument('--dir', type=Path, default=DEFAULT_DIR, help='where kernel and preimages are cached')
    sub = parser.add_subparsers(dest='command', required=True)
    sub.add_parser('prepare')
    run_parser = sub.add_parser('run')
    run_parser.add_argument('--port', type=int, default=8545)
    run_parser.add_argument('--fund', action='append', default=[ALICE_PKH], help='tz address to fund (repeatable)')
    run_parser.add_argument('--min-level', type=int, default=140, help='block level to wait for before returning')
    run_parser.add_argument('--time-between-blocks', type=float, default=1)
    sub.add_parser('stop')
    args = parser.parse_args()

    if args.command == 'prepare':
        prepare(args.dir)
    elif args.command == 'run':
        if not (args.dir / 'kernel' / 'sandbox-installer.wasm').exists():
            prepare(args.dir)
        run(args.dir, args.port, args.fund, args.min_level, args.time_between_blocks)
    else:
        stop()


if __name__ == '__main__':
    main()
