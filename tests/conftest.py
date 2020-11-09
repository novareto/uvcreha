"""
global settings
"""

from io import StringIO
import pytest


ARANGO_CONFIG = '''
arango:
  user: {arango_user}
  password: {arango_password}
  database: {arango_database}
  url: {arango_url}
'''


CONFIG = '''
app:

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
def arangodb(request, config):
    """Create a intermediary docker container a arangodb instance
    """
    import omegaconf
    import docmanager.db

    arango_type = request.config.getoption("--arango")
    arango_user = request.config.getoption("--arango_user")
    arango_password = request.config.getoption("--arango_password")
    arango_database = request.config.getoption("--arango_database")

    if arango_type == 'local':
        arango_url = request.config.getoption("--arango_url")
        config = omegaconf.OmegaConf.create(ARANGO_CONFIG.format(
            arango_user=arango_user,
            arango_password=arango_password,
            arango_database=arango_database,
            arango_url=arango_url,
        ))
        db = docmanager.db.Database(**config.arango)
        db.ensure_database()
        db.session.create_collection(docmanager.db.User)
        yield db
        db.session.drop_collection(docmanager.db.User)
    elif arango_type == 'docker':
        import socket
        import docker

        client = docker.from_env()
        arango_url = 'http://192.168.52.2:8529'
        config = omegaconf.OmegaConf.create(ARANGO_CONFIG.format(
            arango_user=arango_user,
            arango_password=arango_password,
            arango_database=arango_database,
            arango_url=arango_url,
        ))

        container = client.containers.run(
            image="arangodb/arangodb:3.7.3",
            environment={
                "ARANGO_ROOT_PASSWORD": config.arango.password
            },
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

        while True:
            sock = socket.socket()
            try:
                sock.connect(("192.168.52.2", 8529))
                break
            except socket.error:
                pass

        yield docmanager.db.Database(**config.arango)

        mynet.disconnect(container)
        mynet.remove()
        container.stop()
        container.remove()


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

    yield cromlech.session.WSGISessionManager(
        manager, environ_key=config.app.env.session)

    folder.cleanup()


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


def pytest_addoption(parser):
    parser.addoption(
        "--arango", action="store", default="local",
        help="arango: local or docker"
    )

    parser.addoption(
        "--arango_user", action="store", default="root",
        help="arango_user: name of the arango user"
    )

    parser.addoption(
        "--arango_password", action="store", default="openSesame",
        help="arango_password: arango password"
    )

    parser.addoption(
        "--arango_database", action="store", default="tests",
        help="arango_database: arango database"
    )

    parser.addoption(
        "--arango_url", action="store", default="http://127.0.0.1:8529",
        help="arango_url: arango database url"
    )
