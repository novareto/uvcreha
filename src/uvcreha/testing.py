try:
    import pytest
except ImportError:
    pass
else:
    import json
    import pathlib
    import importscan
    import zope.dottedname.resolve
    import uvcreha
    from copy import deepcopy
    from cromlech.session import Store, Session
    from omegaconf import OmegaConf
    from uvcreha.contenttypes import registry
    from uvcreha.database import Connector
    from uvcreha.configure import setup


    def resolve_path(path: str) -> str:
        path = pathlib.Path(path)
        return str(path.resolve())


    class TestUser:

        def __init__(self, user):
            self.user = user

        def login(self, app):
            response = app.post("/login", {
                'loginname': self.user['loginname'],
                'password': self.user['password'],
                'form.trigger': 'trigger.speichern',
            })
            return response


    class UVCRehaTestRunner:

        def __init__(self):
            if not OmegaConf.get_resolver('path'):
                OmegaConf.register_resolver(
                    "path", resolve_path)
            if not OmegaConf.get_resolver('class'):
                OmegaConf.register_resolver(
                    "class", zope.dottedname.resolve.resolve)
            importscan.scan(uvcreha)

        def pytest_addoption(self, parser):
            configfile = (
                pathlib.Path(__file__).parent /
                pathlib.Path('./testing.yaml')
            )
            parser.addoption(
                "--uvcreha_config", action="store_true",
                default=configfile,
                help="uvcreha_config: specify a custom app configuration."
            )

        @pytest.fixture(scope="session")
        def db_init(self, request, arango_config):
            connector = Connector.from_config(**arango_config._asdict())

            if connector._system.has_database(connector.config.database):
                connector._system.delete_database(connector.config.database)
            connector._system.create_database(
                name=connector.config.database,
                users=[{
                    'username': connector.config.user,
                    'password': connector.config.password,
                    'active': True
                }],
            )

            db = connector.get_database()
            for name, ct in registry.items():
                if ct.collection:
                    db.create_collection(ct.collection)
            yield connector
            for name, ct in registry.items():
                if ct.collection:
                    db.delete_collection(ct.collection)
            connector._system.delete_database(connector.config.database)

        @pytest.fixture(scope="session")
        def user(self, db_init):
            # Add the User
            ct = registry['user']
            user = ct.factory(
                uid='123',
                loginname='test',
                password='test',
                permissions=['document.view', 'document.add']
            )
            db = db_init.get_database()
            user['_key'] = user['uid']
            db[ct.collection].insert(dict(user))
            yield TestUser(user)
            db[ct.collection].delete(dict(user))

        @pytest.fixture
        def session(self):

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
        def root(self, request, tmp_path_factory, arango_config, db_init):
            configfile = request.config.getoption("--uvcreha_config")
            config = OmegaConf.load(configfile)
            arango = OmegaConf.create({'arango': arango_config._asdict()})
            conf = OmegaConf.merge(config, arango)
            folder = tmp_path_factory.mktemp('sessions', numbered=True)
            conf.app.session.cache = str(folder)
            root = setup(conf)
            return root


    pytest_uvcreha = UVCRehaTestRunner()
