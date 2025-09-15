import atexit
import logging
import unittest
from concurrent.futures import FIRST_EXCEPTION
from concurrent.futures import Future
from concurrent.futures import ThreadPoolExecutor
from concurrent.futures import wait
from contextlib import suppress
from pprint import pprint
from threading import Event
from time import sleep
from typing import List
from typing import Optional

import requests.exceptions
from testcontainers.core.container import DockerContainer  # type: ignore[import-untyped]
from testcontainers.core.docker_client import DockerClient  # type: ignore[import-untyped]

from pytezos.client import PyTezosClient
from pytezos.operation.group import OperationGroup
from pytezos.sandbox.parameters import LATEST
from pytezos.sandbox.parameters import sandbox_addresses

DOCKER_IMAGE = 'bakingbad/sandboxed-node:v23.2'
MAX_ATTEMPTS = 60
ATTEMPT_DELAY = 0.5
TEZOS_NODE_PORT = 8732


def kill_existing_containers():
    docker = DockerClient()
    running_containers: List[DockerContainer] = docker.client.containers.list(
        filters={
            'status': 'running',
            'ancestor': DOCKER_IMAGE,
        }
    )
    for container in running_containers:
        with suppress(Exception):
            container.stop(timeout=1)


atexit.register(kill_existing_containers)


def worker_callback(f):
    e = f.exception()

    if e is None:
        return

    trace = []
    tb = e.__traceback__
    while tb is not None:
        trace.append(
            {
                "filename": tb.tb_frame.f_code.co_filename,
                "name": tb.tb_frame.f_code.co_name,
                "lineno": tb.tb_lineno,
            }
        )
        tb = tb.tb_next
    pprint(
        {
            'type': type(e).__name__,
            'message': str(e),
            'trace': trace,
        }
    )


def get_next_baker_key(client: PyTezosClient) -> str:
    baking_rights = client.shell.head.helpers.baking_rights()
    delegate = next(br['delegate'] for br in baking_rights if br['round'] == 0)
    return next(k for k, v in sandbox_addresses.items() if v == delegate)


class SandboxedNodeContainer(DockerContainer):
    def __init__(self, image=DOCKER_IMAGE, port=TEZOS_NODE_PORT):
        super().__init__(image)
        self.with_bind_ports(TEZOS_NODE_PORT, port)
        self.url = f'http://localhost:{port}'
        self.client = PyTezosClient().using(shell=self.url)

    def start(self):
        super().start()
        if self.get_wrapped_container() is None:
            raise RuntimeError('Failed to create a container')

    def wait_for_connection(self, max_attempts=MAX_ATTEMPTS, attempt_delay=ATTEMPT_DELAY) -> bool:
        attempts = max_attempts
        while attempts > 0:
            try:
                self.client.shell.node.get("/version/")
                return True
            except requests.exceptions.ConnectionError:
                sleep(attempt_delay)
                attempts -= 1
        return False

    def activate(self, protocol=LATEST):
        return self.client.using(key='dictator').activate_protocol(protocol).fill().sign().inject()

    def bake(self, key: str, min_fee: int = 0):
        return self.client.using(key=key).bake_block(min_fee).fill().work().sign().inject()

    def get_client(self, key: str):
        return self.client.using(key=key)


class SandboxedNodeTestCase(unittest.TestCase):
    """Perform tests with sanboxed node in Docker container."""

    IMAGE: str = DOCKER_IMAGE
    "Docker image to use"

    PORT: int = TEZOS_NODE_PORT
    "Port to expose to host machine"

    PROTOCOL: str = LATEST
    "Hash of protocol to activate"

    node_container: Optional['SandboxedNodeContainer'] = None
    executor: Optional[ThreadPoolExecutor] = None

    @classmethod
    def setUpClass(cls) -> None:
        """Spin up sandboxed node container and activate protocol."""
        kill_existing_containers()
        cls.node_container = SandboxedNodeContainer(image=cls.IMAGE, port=cls.PORT)
        cls.node_container.start()

        if not cls.node_container.wait_for_connection():
            logging.error('failed to connect to %s', cls.node_container.url)
            return

        cls.node_container.activate(cls.PROTOCOL)

    @classmethod
    def tearDownClass(cls) -> None:
        cls._get_node_container().stop(force=True, delete_volume=True)

    @classmethod
    def _get_node_container(cls) -> SandboxedNodeContainer:
        if cls.node_container is None:
            raise RuntimeError('Sandboxed node container is not running')
        return cls.node_container

    @classmethod
    def activate(cls, protocol_alias: str) -> OperationGroup:
        """Activate protocol."""
        return cls._get_node_container().activate(protocol=protocol_alias)

    @classmethod
    def get_client(cls, key='bootstrap2') -> PyTezosClient:
        return cls._get_node_container().get_client(key)

    @classmethod
    def bake_block(cls, min_fee: int = 0) -> OperationGroup:
        """Bake new block.

        :param min_fee: minimum fee of operation to be included in block
        """
        key = get_next_baker_key(cls.get_client())
        return cls._get_node_container().bake(key=key, min_fee=min_fee)

    @property
    def client(self) -> PyTezosClient:
        """PyTezos client to interact with sandboxed node."""
        return self._get_node_container().get_client(key='bootstrap1')


class SandboxedNodeAutoBakeTestCase(SandboxedNodeTestCase):
    exit_event: Optional[Event] = None
    baker: Optional[Future] = None
    min_fee = 0

    TIME_BETWEEN_BLOCKS = 3
    "Time delay between bake attempts, in seconds"

    @staticmethod
    def autobake(time_between_blocks: int, node_url: str, exit_event: Event, min_fee=0):
        logging.info("Baker thread started")
        client = PyTezosClient().using(shell=node_url)
        ptr = 0
        while not exit_event.is_set():
            if ptr % time_between_blocks == 0:
                key = get_next_baker_key(client)
                client.using(key=key).bake_block(min_fee=min_fee).fill().work().sign().inject()
            sleep(1)
            ptr += 1
        logging.info("Baker thread stopped")

    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        if cls.executor is None:
            cls.executor = ThreadPoolExecutor(1)
        if cls.node_container is None:
            raise RuntimeError('sandboxed node container is not created')
        cls.exit_event = Event()
        cls.baker = cls.executor.submit(
            cls.autobake,
            cls.TIME_BETWEEN_BLOCKS,
            cls.node_container.url,
            cls.exit_event,
            cls.min_fee,
        )
        cls.baker.add_done_callback(worker_callback)

    @classmethod
    def tearDownClass(cls) -> None:
        assert cls.exit_event
        assert cls.baker
        cls.exit_event.set()
        wait([cls.baker], return_when=FIRST_EXCEPTION)
