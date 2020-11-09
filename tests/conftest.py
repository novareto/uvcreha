"""
global settings
"""

from io import StringIO
import pytest


READY_PHRASE = (
    b"ArangoDB (version 3.7.3 [linux]) is ready for business. Have fun!\n"
    )


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
def arangodb(request):
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
        cleanup = None

    else:
        import docker
        import time

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

        mynet = client.networks.create(
            "network1",
            driver="bridge",
            ipam=ipam_config
        )

        mynet.connect(container, ipv4_address="192.168.52.2")

        while True:
            logs = container.logs()
            if logs.endswith(READY_PHRASE):
                break
            time.sleep(0.1)

        def cleanup():
            mynet.disconnect(container)
            mynet.remove()
            container.stop()
            container.remove()

        request.addfinalizer(cleanup)

    return docmanager.db.Database(**config.arango)


@pytest.fixture(scope="session")
def application(request, config, arangodb):
    import logging
    import colorlog
    import importscan
    import tempfile
    import docmanager
    import docmanager.auth
    from docmanager.app import application as app

    importscan.scan(docmanager)

    folder = tempfile.TemporaryDirectory()

    def session_middleware(config):
        from pathlib import Path
        import cromlech.session
        import cromlech.sessions.file

        handler = cromlech.sessions.file.FileStore(Path(folder.name), 3000)
        manager = cromlech.session.SignedCookieManager(
            "secret", handler, cookie="my_sid")
        return cromlech.session.WSGISessionManager(
            manager, environ_key=config.session)

    def fanstatic_middleware(config):
        from fanstatic import Fanstatic
        from functools import partial

        return partial(Fanstatic, **config)

    def make_logger(config) -> logging.Logger:
        logger = colorlog.getLogger(config.name)
        logger.setLevel(logging.DEBUG)
        return logger

    app.setup(
        config=config.app,
        database=arangodb,
        logger=make_logger(config.app.logger)
    )

    # Create the needed collections
    arangodb.ensure_database()
    arangodb.session.create_collection(
        docmanager.db.User.__collection__)
    arangodb.session.create_collection(
        docmanager.db.File.__collection__)
    arangodb.session.create_collection(
        docmanager.db.Document.__collection__)

    # Auth
    auth = docmanager.auth.Auth(
        docmanager.db.User(arangodb.session), config.app.env)
    app.plugins.register(auth, name="authentication")

    # Middlewares
    app.middlewares.register(
        fanstatic_middleware(config.app.assets), priority=0)
    app.middlewares.register(
        session_middleware(config.app.env), priority=1)
    app.middlewares.register(auth, priority=2)

    yield app

    # cleanup
    folder.cleanup()
    arangodb.session.delete_collection(
        docmanager.db.Document.__collection__)
    arangodb.session.delete_collection(
        docmanager.db.File.__collection__)
    arangodb.session.delete_collection(
        docmanager.db.User.__collection__)


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
