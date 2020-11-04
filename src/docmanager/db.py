from collections import namedtuple
from contextlib import ContextDecorator
from functools import cached_property
from arango import ArangoClient
from functools import cached_property
from roughrider.validation.types import Validatable
from docmanager.request import Request
import orjson


DB_CONFIG = namedtuple('DB', ['user', 'password', 'database'])


class Transaction(ContextDecorator):

    __slots__ = ('session', 'collection', '_txn')

    def __init__(self, session, collection: str):
        self.session = session
        self.collection = collection
        self._txn = None

    def __enter__(self):
        self._txn = self.session.begin_transaction(
            read=self.collection, write=self.collection)
        return self._txn

    def __exit__(self, exc_type, exc_value, traceback):
        if exc_type:
            self._txn.abort_transaction()
            print(exc_type, exc_value, traceback)
            return False
        self._txn.commit_transaction()
        return True


class Database:

    __slots__ = ('config', 'client')

    def __init__(self, url: str='http://localhost:8529', **config):
        self.config = DB_CONFIG(**config)
        self.client = ArangoClient(
            url, serializer=orjson.dumps, deserializer=orjson.loads)

    @property
    def session(self):
        return self.client.db(
            self.config.database,
            username=self.config.user,
            password=self.config.password
        )

    def transaction(self, collection: str):
        return Transaction(self.session, collection)

    @property
    def system_database(self):
        return self.client.db(
            '_system',
            username=self.config.user,
            password=self.config.password
        )

    def ensure_database(self):
        sys_db = self.system_database
        if not sys_db.has_database(self.config.database):
            sys_db.create_database(self.config.database)

    def delete_database(self):
        sys_db = self.system_database
        if not sys_db.has_database(self.config.database):
            sys_db.delete_database(self.config.database)
