"""
global settings
"""

import pathlib
import omegaconf
import pytest
from zope.dottedname import resolve


omegaconf.OmegaConf.register_resolver("class", resolve.resolve)


CONFIG = omegaconf.OmegaConf.create('''
app:

  factories:
    user: ${class:uvcreha.models.User}
    request: ${class:uvcreha.request.Request}

  env:
    session: uvcreha.test.session
    user: test.principal

  session:
    cookie_name: uvcreha.cookie
    cookie_secret: secret

  logger:
    name: uvcreha.test.logger

  assets:
    compile: True
    recompute_hashes: True
    bottom: True
''')


@pytest.fixture
def session():
    from cromlech.session import Store, Session
    from copy import deepcopy

    class MemoryStore(Store):

        def __init__(self):
            self._store = {}

        def __iter__(self):
            return iter(self._store.keys())

        def touch(self, sid):
            print('Session "%s" was accessed' % sid)

        def get(self, sid):
            """We return a copy, to avoid mutability by reference.
            """
            data = self._store.get(sid)
            if data is not None:
                return deepcopy(data)
            return data

        def set(self, sid, session):
            self._store[sid] = session

        def clear(self, sid):
            if sid in self._store:
                self._store[sid].clear()

        def delete(self, sid):
            del self._store[sid]

    return Session('a sid', MemoryStore(), new=True)


@pytest.fixture(scope="session")
def db_init(arango_config):
    from uvcreha.models import User, File, Document
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
def api_app(request, arango_config, db_init):
    import importscan
    import uvcreha
    from uvcreha.app import api as app

    importscan.scan(uvcreha)
    CONFIG['arango'] = arango_config._asdict()
    app.configure(CONFIG)
    return app


@pytest.fixture(scope="session")
def web_app(request, arango_config, db_init):
    import importscan
    import tempfile
    import uvcreha
    from uvcreha.app import browser as app

    importscan.scan(uvcreha)
    CONFIG['arango'] = arango_config._asdict()
    folder = tempfile.TemporaryDirectory()
    CONFIG.app.session.cache = folder.name
    app.configure(CONFIG)
    yield app
    folder.cleanup()


@pytest.fixture(scope="session")
def user(web_app):
    from uvcreha.models import User
    from collections import namedtuple

    testuser = namedtuple('TestUser', ['user', 'login'])

    # Add the User
    user = User(
        uid='123',
        loginname='test',
        password='test',
        permissions=['document.view', 'document.add']
    )
    db = web_app.connector.get_database()
    db.add(user)

    def login(app):
        response = app.post("/login", {
            'loginname': 'test',
            'password': 'test',
            'trigger.speichern': '1',
        })
        return response

    yield testuser(user=user, login=login)
