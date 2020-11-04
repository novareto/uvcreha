"""
global settings
"""

from io import StringIO
import pytest


CONFIG = '''
app:

  arango:
    user: root
    password: openSesame
    database: pytest
    url: http://192.168.52.2:8529

  env:
    session: docmanager.test.session
    principal: docmanager.test.principal
    user: test.principal

  logger:
    name: docmanager.test.logger

  assets:
    compile: True
    recompute_hashes: True
    bottom: True
'''


@pytest.fixture(scope="session")
def config(request):
    import omegaconf
    return omegaconf.OmegaConf.create(CONFIG)


@pytest.fixture(scope="session")
def docker_arangodb_container(request, config):
    """Create a intermediary docker container a arangodb instance"""

    import socket
    import docker

    client = docker.from_env()

    container = client.containers.run(
        image="arangodb/arangodb:3.7.3",
        environment={"ARANGO_ROOT_PASSWORD": config.app.arango.password},
        detach=True
    )

    ipam_pool = docker.types.IPAMPool(
        subnet='192.168.52.0/24',
        gateway='192.168.52.254'
    )

    ipam_config = docker.types.IPAMConfig(
        pool_configs=[ipam_pool]
    )

    mynet= client.networks.create(
        "network1",
        driver="bridge",
        ipam=ipam_config
    )

    mynet.connect(container, ipv4_address="192.168.52.2")

    def tear_down():
        mynet.disconnect(container)
        mynet.remove()
        container.stop()
        container.remove()

    request.addfinalizer(tear_down)

    # wait for connection
    while True:
        sock = socket.socket()
        try:
            sock.connect(("192.168.52.2", 8529))
            break

        except socket.error:
            pass

    return container


@pytest.fixture(scope="session")
def arangodb(request, config, docker_arangodb_container):
    """set the client factory for the docker container."""

    import docmanager.db
    return docmanager.db.Database(**config.app.arango)


@pytest.fixture(scope="session")
def session_middleware(request, config):
    import tempfile
    from pathlib import Path
    import cromlech.session
    import cromlech.sessions.file

    folder = tempfile.TemporaryDirectory()
    handler = cromlech.sessions.file.FileStore(Path(folder.name), 3000)
    manager = cromlech.session.SignedCookieManager(
        "secret", handler, cookie="my_sid")

    request.addfinalizer(folder.cleanup)

    return cromlech.session.WSGISessionManager(
        manager, environ_key=config.app.env.session)


@pytest.fixture(scope="session")
def application(request, config, arangodb, session_middleware):

    import importscan
    import docmanager
    import docmanager.auth
    import uvcreha.example
    import uvcreha.example.app
    from docmanager.app import application as app

    importscan.scan(docmanager)
    importscan.scan(uvcreha.example)

    app.config = config.app
    app.database = arangodb
    app.request_factory = uvcreha.example.app.CustomRequest

    # Session
    app.middlewares.register(session_middleware, priority=1)

    # Auth
    auth = docmanager.auth.Auth(app.database, app.models, config.app.env)
    app.plugins.register(auth, name="authentication")
    app.middlewares.register(auth, priority=2)

    return app
