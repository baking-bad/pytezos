import io
import logging
import sys
import tarfile
import time
from glob import glob
from os.path import abspath
from os.path import dirname
from os.path import exists
from os.path import join
from os.path import split
from pprint import pformat
from typing import List
from typing import Optional

import click
import docker  # type: ignore

from pytezos import ContractInterface
from pytezos import __version__
from pytezos import pytezos
from pytezos.cli.github import create_deployment
from pytezos.cli.github import create_deployment_status
from pytezos.context.mixin import default_network
from pytezos.logging import DEFAULT_LOGGING_CONFIG
from pytezos.logging import logger
from pytezos.michelson.types.base import generate_pydoc
from pytezos.operation.result import OperationResult
from pytezos.rpc.errors import RpcError
from pytezos.sandbox.node import DOCKER_IMAGE
from pytezos.sandbox.node import TEZOS_NODE_PORT
from pytezos.sandbox.node import SandboxedNodeContainer
from pytezos.sandbox.node import get_next_baker_key
from pytezos.sandbox.parameters import LATEST
from pytezos.sandbox.parameters import protocol_hashes
from pytezos.sandbox.parameters import sandbox_protocols

kernel_js_path = join(dirname(dirname(__file__)), 'assets', 'kernel.js')
kernel_json = {
    "argv": ['pytezos', 'kernel', 'run', "-file", "{connection_file}"],
    "display_name": "Michelson",
    "language": "michelson",
    "codemirror_mode": "michelson",
}

SMARTPY_CLI_IMAGE = 'bakingbad/smartpy-cli'
MAX_BAKE_FAILURES = 5


def make_bcd_link(network, address):
    return f'https://better-call.dev/{network}/{address}'


def get_local_contract_path(path, extension='tz'):
    if path is None:
        files = glob(f'*.{extension}')
        if len(files) != 1:
            raise Exception('No contracts found in working directory, specify --path implicitly')
        path = abspath(files[0])
    if exists(path):
        return path
    return False


def get_contract(path):
    path = get_local_contract_path(path)
    if path:
        contract = ContractInterface.from_file(path)
    else:
        network, address = path.split(':')
        contract = pytezos.using(shell=network).contract(address)
    return contract


def get_docker_client():
    return docker.from_env()


@click.group()
@click.version_option(__version__)
@click.pass_context
def cli(*_args, **_kwargs):
    if not logging.getLogger().hasHandlers():
        logging.config.dictConfig(DEFAULT_LOGGING_CONFIG)


@cli.command(help='Manage contract storage')
@click.option('--action', '-a', type=str, help='One of `schema`, `default`.')
@click.option(
    '--path', '-p', type=str, default=None, help='Path to the .tz file, or the following uri: <network>:<KT-address>'
)
@click.pass_context
def storage(_ctx, action: str, path: Optional[str]) -> None:
    contract = get_contract(path)
    if action == 'schema':
        logger.info(generate_pydoc(type(contract.storage.data), title='storage'))
    elif action == 'default':
        logger.info(pformat(contract.storage.dummy()))
    else:
        raise Exception('Action must be either `schema` or `default`')


@cli.command(help='Manage contract storage')
@click.option('--action', '-a', type=str, default='schema', help='One of `schema`')
@click.option(
    '--path', '-p', type=str, default=None, help='Path to the .tz file, or the following uri: <network>:<KT-address>'
)
@click.pass_context
def parameter(_ctx, action: str, path: Optional[str]) -> None:
    contract = get_contract(path)
    if action == 'schema':
        logger.info(contract.parameter.__doc__)
    else:
        raise Exception('Action must be `schema`')


@cli.command(help='Activate and reveal key from the faucet file')
@click.option('--path', '-p', type=str, help='Path to the .json file downloaded from https://faucet.tzalpha.net/')
@click.option('--network', '-n', type=str, default=default_network, help='Default is florencenet')
@click.pass_context
def activate(_ctx, path: str, network: str) -> None:
    ptz = pytezos.using(key=path, shell=network)
    logger.info(
        'Activating %s in the %s',
        ptz.key.public_key_hash(),
        network,
    )

    if ptz.balance() == 0:
        try:
            opg = ptz.reveal().autofill().sign()
            logger.info('Injecting reveal operation:')
            logger.info(pformat(opg.json_payload()))
            opg.inject(_async=False)
        except RpcError as e:
            logger.critical(pformat(e))
            sys.exit(-1)
        else:
            logger.info('Activation succeeded! Claimed balance: %s ꜩ', ptz.balance())
    else:
        logger.info('Already activated')

    try:
        opg = ptz.reveal().autofill().sign()
        logger.info('Injecting reveal operation:')
        logger.info(pformat(opg.json_payload()))
        opg.inject(_async=False)
    except RpcError as e:
        logger.critical(pformat(e))
        sys.exit(-1)
    else:
        logger.info('Your key %s is now active and revealed', ptz.key.public_key_hash())


@cli.command(help='Deploy contract to the specified network')
@click.option('--path', '-p', type=str, help='Path to the .tz file')
@click.option('--storage', type=str, default=None, help='Storage in JSON format (not Micheline)')
@click.option('--network', '-n', type=str, default=default_network, help='Default is florencenet')
@click.option('--key', type=str, default=None)
@click.option('--github-repo-slug', type=str, default=None)
@click.option('--github-oauth-token', type=str, default=None)
@click.option('--dry-run', type=bool, default=False, help='Set this flag if you just want to see what would happen')
@click.pass_context
def deploy(
    _ctx,
    path: str,
    storage: Optional[str],  # pylint: disable=redefined-outer-name
    network: str,
    key: Optional[str],
    github_repo_slug: Optional[str],
    github_oauth_token: Optional[str],
    dry_run: bool,
):
    ptz = pytezos.using(shell=network, key=key)
    logger.info('Deploying contract using %s in the %s', ptz.key.public_key_hash(), network)

    contract = get_contract(path)
    try:
        opg = ptz.origination(script=contract.script(initial_storage=storage)).autofill().sign()
        logger.info('Injecting origination operation:')
        logger.info(pformat(opg.json_payload()))

        if dry_run:
            logger.info(pformat(opg.preapply()))
            sys.exit(0)
        else:
            opg = opg.inject(_async=False)
    except RpcError as e:
        logger.critical(pformat(e))
        sys.exit(-1)
    else:
        originated_contracts = OperationResult.originated_contracts(opg)
        if len(originated_contracts) != 1:
            raise Exception('Operation group must has exactly one originated contract')
        bcd_link = make_bcd_link(network, originated_contracts[0])
        logger.info('Contract was successfully deployed: %s', bcd_link)

        if github_repo_slug:
            deployment = create_deployment(
                github_repo_slug,
                github_oauth_token,
                environment=network,
            )
            logger.info(pformat(deployment))
            status = create_deployment_status(
                github_repo_slug,
                github_oauth_token,
                deployment_id=deployment['id'],
                state='success',
                environment=network,
                environment_url=bcd_link,
            )
            logger.info(status)


@cli.command(help='Update containerized SmartPy CLI')
@click.option('--tag', '-t', type=str, help='Version or tag to pull', default='latest')
@click.pass_context
def update_smartpy(ctx, tag):
    client = get_docker_client()
    logger.info('Will now pull latest SmartPy image, please stay put.')
    for line in client.api.pull(f'{SMARTPY_CLI_IMAGE}:{tag}', stream=True, decode=True):
        logger.info(line)
    logger.info('Pulled SmartPy CLI image successfully!')


def run_smartpy_container(
    tag: str = 'latest',
    command: str = '',
    files_to_add: Optional[List[str]] = None,
    mounts: Optional[List[docker.types.Mount]] = None,
):
    try:
        client = get_docker_client()
        container = client.containers.create(
            image=f'{SMARTPY_CLI_IMAGE}:{tag}',
            command=command,
            detach=True,
            mounts=mounts or [],
        )
        buffer = io.BytesIO()
        with tarfile.open(fileobj=buffer, mode='w:gz') as archive:
            for filename in files_to_add or []:
                with open(filename, 'rb') as current_file:
                    current_file_data = current_file.read()
                    current_file_buffer = io.BytesIO(initial_bytes=current_file_data)
                    _, short_filename = split(filename)
                    archive.add(filename, arcname=short_filename)
        buffer.seek(0)
        container.put_archive(
            '/root/smartpy-cli/',
            buffer,
        )
        container.start()
        return container
    except docker.errors.ImageNotFound:
        logger.error('SmartPy compiler not found. Please run update-smartpy first.')


@cli.command(help='Run SmartPy CLI command "test"')
@click.option('--script', '-s', type=str, help='Path to script', default='script.py')
@click.option('--output-directory', '-o', type=str, help='Output directory', default='./smartpy-output')
@click.option(
    '--protocol', type=click.Choice(['delphi', 'edo', 'florence', 'proto10']), help='Protocol to use', default='edo'
)
@click.option('--detach', '-d', type=bool, help='Run container in detached mode', default=False)
@click.option('--tag', '-t', type=str, help='Version or tag of SmartPy to use', default='latest')
@click.pass_context
def smartpy_test(
    _ctx,
    script: str,
    output_directory: str,
    detach: bool,
    protocol: str,
    tag: str,
):
    client = get_docker_client()
    path = get_local_contract_path(script, extension='py')
    if path:
        _, script_name = split(path)
        container = run_smartpy_container(
            tag=tag,
            command=f'test /root/smartpy-cli/{script_name} /root/output --protocol {protocol}',
            files_to_add=[path],
            mounts=[
                docker.types.Mount(
                    target='/root/output',
                    source=output_directory,
                    type='bind',
                )
            ],
        )
        if container is None:
            raise Exception('Could not create container. Try running update-smartpy.')
        if not detach:
            for line in container.logs(stream=True):
                print(line.decode('utf-8').rstrip())
    else:
        logger.error('No local script found. Please ensure a valid script is present or specify path.')


@cli.command(help='Run SmartPy CLI command "compile"')
@click.option('--script', '-s', type=str, help='Path to script', default='script.py')
@click.option('--output-directory', '-o', type=str, help='Output directory', default='./smartpy-output')
@click.option('--detach', '-d', type=bool, help='Run container in detached mode', default=False)
@click.option(
    '--protocol', type=click.Choice(['delphi', 'edo', 'florence', 'proto10']), help='Protocol to use', default='edo'
)
@click.option('--tag', '-t', type=str, help='Version or tag of SmartPy to use', default='latest')
@click.pass_context
def smartpy_compile(
    _ctx,
    script: str,
    output_directory: str,
    detach: bool,
    protocol: str,
    tag: str,
):
    client = get_docker_client()
    path = get_local_contract_path(script, extension='py')
    if path:
        _, script_name = split(path)
        container = run_smartpy_container(
            tag=tag,
            command=f'compile /root/smartpy-cli/{script_name} /root/output --protocol {protocol}',
            files_to_add=[path],
            mounts=[
                docker.types.Mount(
                    target='/root/output',
                    source=output_directory,
                    type='bind',
                )
            ],
        )
        if container is None:
            raise Exception('Could not create container. Try running update-smartpy.')
        if not detach:
            for line in container.logs(stream=True):
                print(line.decode('utf-8').rstrip())
    else:
        logger.error('No local script found. Please ensure a valid script is present or specify path.')


@cli.command(help='Run containerized sandbox node')
@click.option('--image', type=str, help='Docker image to use', default=DOCKER_IMAGE)
@click.option(
    '--protocol',
    type=click.Choice(list(sandbox_protocols)),
    help='Protocol to use',
    default=next(name for name, value in sandbox_protocols.items() if value == LATEST),
)
@click.option('--port', '-p', type=int, help='Port to expose', default=TEZOS_NODE_PORT)
@click.option('--interval', '-i', type=float, help='Interval between baked blocks (in seconds)', default=1.0)
@click.option('--blocks', '-b', type=int, help='Number of blocks to bake before exit')
@click.pass_context
def sandbox(
    _ctx,
    image: str,
    protocol: str,
    port: int,
    interval: float,
    blocks: int,
):
    protocol_hash = protocol_hashes[protocol]

    node = SandboxedNodeContainer(image=image, port=port)
    with node:
        if not node.wait_for_connection():
            raise TimeoutError('Failed to connect to the sandboxed node')

        logger.info('Activating protocol %s...', protocol_hash)
        node.activate(protocol_hash)

        blocks_baked, failures = 0, 0
        while True:
            try:
                logger.info('Baking block %s...', blocks_baked)
                block_hash = node.bake(key=get_next_baker_key(node.client))
                logger.info('Baked block: %s', block_hash)
                blocks_baked, failures = blocks_baked + 1, 0
                if blocks and blocks_baked == blocks:
                    break
                time.sleep(interval)
            except KeyboardInterrupt:
                break
            except RpcError as e:
                # A long-running sandbox should outlive a single bad answer from the node.
                failures += 1
                if failures > MAX_BAKE_FAILURES:
                    raise
                logger.info('Bake attempt failed (%s/%s): %s', failures, MAX_BAKE_FAILURES, e)
                time.sleep(interval)


@cli.command(help='Update Ligo compiler (docker pull ligolang/ligo)')
@click.option('--tag', '-t', type=str, help='Version or tag to pull', default='0.13.0')
@click.pass_context
def update_ligo(
    _ctx,
    tag: str,
):
    client = get_docker_client()

    logger.info(f'Pulling ligolang/ligo{(":" + tag) if tag else ""}, please stay put.')
    for line in client.api.pull('ligolang/ligo', tag=tag, stream=True, decode=True):
        logger.info(line)
    logger.info('Pulled Ligo compiler image successfully!')


def run_ligo_container(
    tag: str = '0.13.0',
    command: str = '',
    files_to_add: Optional[List[str]] = None,
):
    try:
        client = get_docker_client()
        container = client.containers.create(
            image=f'ligolang/ligo:{tag}',
            command=command,
            detach=True,
        )
        buffer = io.BytesIO()
        with tarfile.open(fileobj=buffer, mode='w:gz') as archive:
            for filename in files_to_add or []:
                with open(filename, 'rb') as current_file:
                    current_file_data = current_file.read()
                    current_file_buffer = io.BytesIO(initial_bytes=current_file_data)
                    _, short_filename = split(filename)
                    archive.add(filename, arcname=short_filename)
        buffer.seek(0)
        container.put_archive(
            '/root/',
            buffer,
        )
        container.start()
        return container
    except docker.errors.ImageNotFound:
        logger.error('Ligo compiler not found. Please run update-ligo first.')


@cli.command(help='Compile contract using Ligo compiler.')
@click.option('--tag', '-t', type=str, help='Version or tag of Ligo compiler', default='0.13.0')
@click.option('--path', '-p', type=str, help='Path to contract')
@click.option('--entry-point', '-ep', type=str, help='Entrypoint for the invocation')
@click.option('--detach', '-d', type=bool, help='Run container in detached mode', default=False)
@click.pass_context
def ligo_compile_contract(
    _ctx,
    tag: str,
    path: str,
    entry_point: str,
    detach: bool,
):
    path = get_local_contract_path(path, extension='ligo')
    if path:
        _, contract_name = split(path)
        container = run_ligo_container(
            tag=tag,
            command=f'compile-contract {contract_name} "{entry_point}"',
            files_to_add=[path],
        )
        if not detach:
            for line in container.logs(stream=True):
                print(line.decode('utf-8').rstrip())
    else:
        logger.error('No local contract found. Please ensure a valid contract is present or specify path.')


@cli.command(help='Define initial storage using Ligo compiler.')
@click.option('--tag', '-t', type=str, help='Version or tag of Ligo compiler', default='0.13.0')
@click.option('--path', '-p', type=str, help='Path to contract')
@click.option('--entry-point', '-ep', type=str, help='Entrypoint for the storage', default='')
@click.option('--expression', '-ex', type=str, help='Expression for the storage', default='')
@click.option('--detach', '-d', type=bool, help='Run container in detached mode', default=False)
@click.pass_context
def ligo_compile_storage(
    _ctx,
    tag: str,
    path: str,
    entry_point: str,
    expression: str,
    detach: bool,
):
    path = get_local_contract_path(path, extension='ligo')
    if path:
        container = run_ligo_container(
            tag=tag,
            command=f'compile-storage {path} "{entry_point}" "{expression}"',
            files_to_add=[path],
        )
        if not detach:
            for line in container.logs(stream=True):
                print(line.decode('utf-8').rstrip())
    else:
        logger.error('No local contract found. Please ensure a valid contract is present or specify path.')


@cli.command(help='Invoke a contract with a parameter using Ligo compiler.')
@click.option('--tag', '-t', type=str, help='Version or tag of Ligo compiler', default='0.13.0')
@click.option('--path', '-p', type=str, help='Path to contract')
@click.option('--entry-point', '-ep', type=str, help='Entrypoint for the invocation')
@click.option('--expression', '-ex', type=str, help='Expression for the invocation')
@click.option('--detach', '-d', type=bool, help='Run container in detached mode', default=False)
@click.pass_context
def ligo_invoke_contract(
    _ctx,
    tag: str,
    path: str,
    entry_point: str,
    expression: str,
    detach: bool,
):
    path = get_local_contract_path(path, extension='ligo')
    if path:
        container = run_ligo_container(
            tag=tag,
            command=f'compile-parameter {path} "{entry_point}" "{expression}"',
            files_to_add=[path],
        )
        if not detach:
            for line in container.logs(stream=True):
                print(line.decode('utf-8').rstrip())
    else:
        logger.error('No local contract found. Please ensure a valid contract is present or specify path.')


if __name__ == '__main__':
    cli(prog_name='pytezos')
