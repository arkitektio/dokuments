import pytest
from dokker import testing, Deployment
from dokker.log_watcher import LogWatcher
import os
import socket
from typing import Generator
from dokuments.dokuments import Dokuments
from rath.links.auth import ComposedAuthLink
from rath.links.aiohttp import AIOHttpLink
from rath.links.graphql_ws import GraphQLWSLink
from rath.links.timeout import TimeoutLink
from rath.links.compose import compose
from rath.links.dictinglink import DictingLink
from rath.links.file import FileExtraction
from dokuments.datalayer import DataLayer
from dokuments.links.upload import UploadLink
from dokuments.rath import (
    DokumentsRath,
    SplitLink,
)
from graphql import OperationType
from dataclasses import dataclass

project_path = os.path.join(os.path.dirname(__file__), "integration")
docker_compose_file = os.path.join(project_path, "docker-compose.yml")


def _reserve_free_ports(count: int) -> list[int]:
    """Ask the OS for `count` distinct free TCP ports.

    All sockets are held open until every port has been assigned, so the kernel
    cannot hand out the same port twice within one call. They are released before
    compose binds them: a race in theory, but the ephemeral range is large.
    """
    sockets: list[socket.socket] = []
    try:
        for _ in range(count):
            sock = socket.socket()
            sock.bind(("127.0.0.1", 0))
            sockets.append(sock)
        return [int(sock.getsockname()[1]) for sock in sockets]
    finally:
        for sock in sockets:
            sock.close()


@pytest.fixture(scope="session")
def integration_ports() -> Generator[dict[str, int], None, None]:
    """Pick this run's host ports and point compose at them.

    `testing()` gives every run a compose project of its own, but two projects
    still cannot bind one host port, and every client package used to pin 6888
    and 6889. The ports are reserved here rather than left to docker because
    `Deployment.spec` is what `docker compose config` renders, which does not
    know a port docker has yet to pick.
    """
    service_port, rustfs_port = _reserve_free_ports(2)
    env = {"DOKUMENTS_HOST_PORT": str(service_port), "RUSTFS_HOST_PORT": str(rustfs_port)}
    previous = {key: os.environ.get(key) for key in env}
    os.environ.update(env)
    try:
        yield {"dokuments": service_port, "rustfs": rustfs_port}
    finally:
        for key, value in previous.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value


async def token_loader() -> str:
    """Load a static token. that is defined in the dokuments.yaml file."""
    return "test"


@dataclass
class DeployedDokuments:
    """Deployed Dokuments instance."""

    deployment: Deployment
    dokuments_watcher: LogWatcher
    dokuments: Dokuments


@pytest.fixture(scope="session")
def deployed_app(integration_ports: dict[str, int]) -> Generator[DeployedDokuments, None, None]:
    """Fixture to deploy the Dokuments application using Docker Compose.

    A `testing()` stack: a compose project of its own on this run's ports, taken
    down again when the session ends.
    """
    setup = testing(docker_compose_file)
    setup.add_health_check(
        url=lambda spec: f"http://localhost:{spec.find_service('dokuments').get_port_for_internal(80).published}/graphql",
        service="dokuments",
        timeout=5,
        max_retries=10,
    )

    watcher = setup.create_watcher("dokuments")

    with setup:
        # Entering a Deployment does nothing (dokker >= 2.6): the spec has to be
        # resolved before any port lookup, or `setup.spec` raises NotInspectedError.
        # No `pull()`: `up()` fetches what is missing, and the stack's ollama image is
        # several gigabytes to fetch again on every run.
        setup.inspect()

        http_url = f"http://localhost:{setup.spec.find_service('dokuments').get_port_for_internal(80).published}/graphql"
        ws_url = f"ws://localhost:{setup.spec.find_service('dokuments').get_port_for_internal(80).published}/graphql"

        print(f"HTTP URL: {http_url}")
        print(f"WS URL: {ws_url}")

        # Uploads go straight to the stack's rustfs, as the service's datalayer alias would.
        datalayer = DataLayer(
            endpoint_url=f"http://localhost:{setup.spec.find_service('rustfs').get_port_for_internal(9000).published}"
        )

        y = DokumentsRath(
            link=compose(
                FileExtraction(),
                DictingLink(),
                UploadLink(datalayer=datalayer),
                TimeoutLink(timeout=12),
                ComposedAuthLink(
                    token_loader=token_loader, token_refresher=token_loader
                ),
                SplitLink(
                    left=AIOHttpLink(endpoint_url=http_url),
                    right=GraphQLWSLink(ws_endpoint_url=ws_url),
                    split=lambda o: o.node.operation != OperationType.SUBSCRIPTION,
                ),
            ),
        )

        dokuments = Dokuments(
            rath=y,
            datalayer=datalayer,
        )

        setup.up()

        setup.check_health()

        with dokuments as dokuments:
            deployed = DeployedDokuments(
                deployment=setup,
                dokuments_watcher=watcher,
                dokuments=dokuments,
            )

            yield deployed
