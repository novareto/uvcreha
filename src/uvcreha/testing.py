try:
    import pytest
except ImportError:
    pass
else:
    from pathlib import Path
    from copy import deepcopy
    from cromlech.session import Store, Session
    from horsebox.project import DefaultProject
    from hyperpyyaml import load_hyperpyyaml
    from uvcreha.contenttypes import registry


    class TestUser:
        def __init__(self, user):
            self.user = user

        def login(self, app):
            response = app.post(
                "/login",
                {
                    "loginname": self.user["loginname"],
                    "password": self.user["password"],
                    "form.trigger": "trigger.speichern",
                },
            )
            return response


    class UVCRehaTestRunner:

        def pytest_addoption(self, parser):
            configfile = Path(__file__).parent / Path("./testing.yaml")
            parser.addoption(
                "--uvcreha_config",
                action="store_true",
                default=configfile,
                help="uvcreha_config: specify a custom app configuration.",
            )

        @pytest.fixture(scope="session")
        def user(self, arangodb):
            # Add the User
            ct = registry["user"]
            user = ct.factory(
                uid="123",
                loginname="test",
                password="test",
                permissions=["document.view", "document.add"],
            )
            db = arangodb.get_database()
            if not db.has_collection(ct.collection):
                db.create_collection(ct.collection)
            user["_key"] = user["uid"]
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
                    """We return a copy, to avoid mutability by reference."""
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

            return Session("a sid", MemoryStore(), new=True)

        @pytest.fixture(scope="session")
        def config(self, request, tmp_path_factory, arangodb):
            configfile = request.config.getoption("--uvcreha_config")
            folder = tmp_path_factory.mktemp("sessions", numbered=True)
            override = {
                "session": {
                    "cache": str(folder)
                },
                "arango": {
                    **arangodb.config._asdict()
                }
            }
            with configfile.open('r') as f:
                config: dict = load_hyperpyyaml(f, overrides=override)

            project = DefaultProject.from_config(config)
            for loader in project.loaders:
                loader()
            return config

        @pytest.fixture(scope="session")
        def uvcreha(self, config):
            return config['uvcreha']

        @pytest.fixture(scope="session")
        def webapp(self, config):
            return config['app']

    pytest_uvcreha = UVCRehaTestRunner()
