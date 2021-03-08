import pytest


@pytest.fixture
def session():
    from copy import deepcopy
    from cromlech.session import Store, Session

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
