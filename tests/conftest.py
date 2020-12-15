"""
global settings
"""

from io import StringIO
import omegaconf
import pytest


CONFIG = omegaconf.OmegaConf.create('''
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
''')


@pytest.fixture(scope="session")
def db_connector(arango_config):
    from docmanager.models import User, File, Document
    from reiter.arango.connector import Connector

    connector = Connector(**arango_config._asdict())
    db = connector.get_database()
    db.db.create_collection(User.__collection__)
    db.db.create_collection(File.__collection__)
    db.db.create_collection(Document.__collection__)
    yield connector
    db.db.delete_collection(User.__collection__)
    db.db.delete_collection(File.__collection__)
    db.db.delete_collection(Document.__collection__)


@pytest.fixture(scope="session")
def api_app(request, db_connector):
    import importscan
    import docmanager
    from docmanager.app import api as app
    from docmanager.models import User, Document, File

    importscan.scan(docmanager)

    app.connector = db_connector
    app.config.update(CONFIG.app)
    return app


@pytest.fixture(scope="session")
def web_app(request, db_connector):
    import logging
    import colorlog
    import importscan
    import tempfile
    import docmanager
    import docmanager.auth
    import docmanager.flash
    from docmanager.models import User
    from docmanager.mq import AMQPEmitter
    from docmanager.app import browser as app

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
            manager, environ_key=CONFIG.app.env.session)

    def fanstatic_middleware(config):
        from fanstatic import Fanstatic
        from functools import partial

        return partial(Fanstatic, **config)

    def make_logger(config) -> logging.Logger:
        logger = colorlog.getLogger(CONFIG.name)
        logger.setLevel(logging.DEBUG)
        return logger

    app.connector = db_connector
    app.config.update(CONFIG.app)

    # AMQP
    amqp = AMQPEmitter(CONFIG.amqp)
    app.plugins.register(amqp, name="amqp")

    # Auth
    db = db_connector.get_database()
    auth = docmanager.auth.Auth(db(User), CONFIG.app.env)
    app.plugins.register(auth, name="authentication")

    # Middlewares
    app.middlewares.register(auth, order=0)
    app.middlewares.register(
        session_middleware(CONFIG.app.env), order=1)
    app.middlewares.register(
        fanstatic_middleware(CONFIG.app.assets), order=2)

    yield app
    folder.cleanup()


@pytest.fixture(scope="session")
def user(db_connector):
    from docmanager.models import User
    from functools import partial
    from collections import namedtuple

    testuser = namedtuple('TestUser', ['user', 'login'])

    # Add the User
    user = User(
        username='test',
        password='test',
        permissions=['document.view', 'document.add']
    )
    db = db_connector.get_database()
    db.add(user)

    def login(app):
        response = app.post("/login", {
            'username': 'test',
            'password': 'test',
            'trigger.speichern': '1',
        })
        return response

    yield testuser(user=user, login=login)
