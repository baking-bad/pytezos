from typing import Any
from typing import Dict
from typing import List
from typing import Optional

import pytest
from docker.errors import DockerException  # type: ignore[import-untyped]
from testcontainers.core.labels import LABEL_SESSION_ID  # type: ignore[import-untyped]
from testcontainers.core.labels import SESSION_ID  # type: ignore[import-untyped]

from pytezos.sandbox import node
from pytezos.sandbox.node import SANDBOX_PORT_ENV
from pytezos.sandbox.node import TEZOS_NODE_PORT
from pytezos.sandbox.node import SandboxedNodeContainer
from pytezos.sandbox.node import SandboxPortConflict
from pytezos.sandbox.node import ensure_port_free
from pytezos.sandbox.node import kill_own_containers
from pytezos.sandbox.node import publishes_host_port
from pytezos.sandbox.node import sandbox_port

Ports = Optional[Dict[str, Any]]


def bound(*host_ports: int) -> Ports:
    return {'8732/tcp': [{'HostIp': '0.0.0.0', 'HostPort': str(p)} for p in host_ports], '9732/tcp': None}


class FakeContainer:
    def __init__(
        self,
        ports: Ports = None,
        labels: Optional[Dict[str, str]] = None,
        name='funny_jepsen',
        short_id='5801d0ed494d',
    ):
        self.ports = ports
        self.labels = labels or {}
        self.name = name
        self.short_id = short_id
        self.remove_calls: List[Dict[str, Any]] = []
        self.stop_calls: List[Dict[str, Any]] = []

    def remove(self, **kwargs):
        self.remove_calls.append(kwargs)

    def stop(self, **kwargs):
        self.stop_calls.append(kwargs)


class FakeDocker:
    def __init__(self, containers: Optional[List[FakeContainer]] = None):
        self._containers = containers or []
        self.filters: Optional[Dict[str, str]] = None
        self.containers = self

    def list(self, filters=None):
        self.filters = filters
        return list(self._containers)


class FakeDockerClient:
    def __init__(self, **kwargs):
        self.client = FakeDocker()


def test_sandbox_port_defaults_to_8732(monkeypatch):
    monkeypatch.delenv(SANDBOX_PORT_ENV, raising=False)
    assert sandbox_port() == TEZOS_NODE_PORT == 8732


def test_sandbox_port_reads_env(monkeypatch):
    monkeypatch.setenv(SANDBOX_PORT_ENV, '18732')
    assert sandbox_port() == 18732


def test_sandbox_port_rejects_garbage(monkeypatch):
    monkeypatch.setenv(SANDBOX_PORT_ENV, 'abc')
    with pytest.raises(ValueError, match=r"PYTEZOS_SANDBOX_PORT must be a port number, got 'abc'"):
        sandbox_port()


@pytest.mark.parametrize(
    'ports, port, expected',
    [
        (bound(8732), 8732, True),
        (bound(18732), 8732, False),
        (bound(18732), 18732, True),
        (bound(8732, 18732), 18732, True),
        ({'5432/tcp': [{'HostIp': '::', 'HostPort': '8732'}]}, 8732, True),
        ({'8732/tcp': None}, 8732, False),
        ({}, 8732, False),
        (None, 8732, False),
    ],
)
def test_publishes_host_port(ports, port, expected):
    assert publishes_host_port(FakeContainer(ports=ports), port) is expected


def test_ensure_port_free_no_container():
    docker = FakeDocker()
    ensure_port_free(docker, 8732)
    assert docker.filters == {'status': 'running'}


def test_ensure_port_free_ignores_containers_on_other_ports():
    other = FakeContainer(ports=bound(8732), labels={LABEL_SESSION_ID: 'other-process'})
    ensure_port_free(FakeDocker([other]), 18732)
    assert other.remove_calls == []


def test_ensure_port_free_raises_on_foreign_container():
    foreign = FakeContainer(ports=bound(8732), labels={LABEL_SESSION_ID: 'other-process'})
    with pytest.raises(SandboxPortConflict, match=r'8732.*funny_jepsen.*5801d0ed494d'):
        ensure_port_free(FakeDocker([foreign]), 8732)
    assert foreign.remove_calls == []


def test_ensure_port_free_raises_on_unlabelled_container():
    other = FakeContainer(ports=bound(8732), labels={}, name='postgres', short_id='0123456789ab')
    with pytest.raises(SandboxPortConflict, match=r'8732.*postgres.*0123456789ab'):
        ensure_port_free(FakeDocker([other]), 8732)
    assert other.remove_calls == []


def test_ensure_port_free_removes_own_stale_container():
    stale = FakeContainer(ports=bound(8732), labels={LABEL_SESSION_ID: SESSION_ID})
    ensure_port_free(FakeDocker([stale]), 8732)
    assert stale.remove_calls == [{'force': True, 'v': True}]


def test_container_binds_host_port(monkeypatch):
    monkeypatch.setattr('testcontainers.core.container.DockerClient', FakeDockerClient)
    container = SandboxedNodeContainer(port=18732)
    assert container.ports == {TEZOS_NODE_PORT: 18732}
    assert container.port == 18732
    assert container.url.endswith(':18732')


def test_start_raises_on_conflict_without_registering(monkeypatch):
    monkeypatch.setattr('testcontainers.core.container.DockerClient', FakeDockerClient)
    monkeypatch.setattr(node, '_started_here', [])
    container = SandboxedNodeContainer(port=18732)
    container.get_docker_client().client = FakeDocker([FakeContainer(ports=bound(18732))])
    with pytest.raises(SandboxPortConflict):
        container.start()
    assert node._started_here == []


def test_kill_own_containers_stops_only_registered(monkeypatch):
    class Raising(FakeContainer):
        def stop(self, **kwargs):
            super().stop(**kwargs)
            raise RuntimeError('already gone')

    first, second, third = Raising(), FakeContainer(), FakeContainer()
    monkeypatch.setattr(node, '_started_here', [first, second])
    kill_own_containers()
    assert first.stop_calls == [{'force': True, 'delete_volume': True}]
    assert second.stop_calls == [{'force': True, 'delete_volume': True}]
    assert third.stop_calls == []


def test_kill_own_containers_with_empty_registry_touches_nothing(monkeypatch):
    def no_docker(**kwargs):
        raise DockerException('must not be called')

    monkeypatch.setattr(node, 'DockerClient', no_docker)
    monkeypatch.setattr('testcontainers.core.container.DockerClient', no_docker)
    monkeypatch.setattr(node, '_started_here', [])
    kill_own_containers()


def test_stop_deregisters(monkeypatch):
    monkeypatch.setattr('testcontainers.core.container.DockerClient', FakeDockerClient)
    stopped: List[Dict[str, Any]] = []
    monkeypatch.setattr(node.DockerContainer, 'stop', lambda self, **kwargs: stopped.append(kwargs))
    container = SandboxedNodeContainer(port=18732)
    monkeypatch.setattr(node, '_started_here', [container])

    container.stop(force=True, delete_volume=True)
    assert node._started_here == []
    container.stop(force=True, delete_volume=True)
    assert stopped == [{'force': True, 'delete_volume': True}] * 2
