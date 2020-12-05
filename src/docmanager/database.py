import abc
from collections import namedtuple
from contextlib import ContextDecorator
from functools import wraps
from typing import Iterable, List, Optional, ClassVar

import arango
import orjson
import pydantic

import horseman.http
from contextlib import contextmanager
from docmanager import registries
from docmanager.validation import catch_pydantic_exception


DB_CONFIG = namedtuple('DB', ['user', 'password', 'database'])


class BindingError(Exception):
    pass


@contextmanager
def transaction(session, collection):
    transaction = session.begin_transaction(exclusive=collection)
    try:
        yield transaction
        transaction.commit_transaction()
    except Exception as exc:
        transaction.abort_transaction()
        raise


def mydump(v, *args, **kwargs):
    if 'password' in v:
        if isinstance(v['password'], pydantic.types.SecretStr):
            v['password'] = v['password'].get_secret_value()
    return orjson.dumps(v)


class Database:

    __slots__ = ('config', 'client')

    def __init__(self, url: str = 'http://localhost:8529', **config):
        self.config = DB_CONFIG(**config)
        self.client = arango.ArangoClient(
            url, serializer=mydump, deserializer=orjson.loads)

    @property
    def session(self):
        return self.client.db(
            self.config.database,
            username=self.config.user,
            password=self.config.password
        )

    def query(self, model):
        return DBBinding(model, self.session)

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


class DBBinding:

    def __init__(self, model, session):
        self.session = session
        self.model = model

    @property
    def collection(self):
        return self.model.__collection__

    def add(self, item):
        assert isinstance(item, self.model)
        assert not item.bound
        try:
            with transaction(self.session, self.collection) as txn:
                collection = txn.collection(self.collection)
                response = collection.insert(item.dict())
                item.bind(
                    self,
                    id=response["_id"],
                    key=response["_key"],
                    rev=response["_rev"]
                )
        except arango.exceptions.DocumentInsertError as exc:
            raise horseman.http.HTTPError(exc.http_code, exc.message)
        return item

    def find(self, **filters) -> List[pydantic.BaseModel]:
        collection = self.session.collection(self.collection)
        return [self.model.spawn(self, **data)
                for data in collection.find(filters)]

    def find_one(self, **filters) -> Optional[pydantic.BaseModel]:
        collection = self.session.collection(self.collection)
        found = collection.find(filters, limit=1)
        if not found.count():
            return None
        data = found.next()
        return self.model.spawn(self, **data)

    def fetch(self, key) -> Optional[pydantic.BaseModel]:
        collection = self.session.collection(self.collection)
        if (data := collection.get(key)) is not None:
            return self.model.spawn(self, **data)

    def exists(self, key) -> bool:
        collection = self.session.collection(self.collection)
        return collection.has({"_key": key})

    def delete(self, key) -> bool:
        try:
            with transaction(self.session, self.collection) as txn:
                collection = txn.collection(self.collection)
                collection.delete(key)
        except arango.exceptions.DocumentDeleteError as exc:
            raise horseman.http.HTTPError(exc.http_code, exc.message)
        return True

    def update(self, key, **data) -> str:
        try:
            with transaction(self.session, self.collection) as txn:
                collection = txn.collection(self.collection)
                data = {'_key': key, **data}
                response = collection.update(data)
                return response["_rev"]
        except arango.exceptions.DocumentUpdateError as exc:
            raise horseman.http.HTTPError(exc.http_code, exc.message)
        return True

    def replace(self, item) -> bool:
        try:
            with transaction(self.session, self.collection) as txn:
                collection = txn.collection(self.collection)
                data = item.dict()
                response = collection.replace(data)
                item.rev = response["_rev"]
        except arango.exceptions.DocumentUpdateError as exc:
            raise horseman.http.HTTPError(exc.http_code, exc.message)
        return True


class DBModel(pydantic.BaseModel):

    id: Optional[str] = pydantic.Field(alias="_id")
    key: Optional[str] = pydantic.Field(alias="_key")
    rev: Optional[str] = pydantic.Field(alias="_rev")

    __collection__: ClassVar[str]
    _binding = pydantic.PrivateAttr(default=None)

    def bind(self, binding, id=..., key=..., rev=...):
        assert not self.bound
        if self.id != ...:
            self.id = id
        if self.key != ...:
            self.key = key
        if self.rev != ...:
            self.rev = rev
        self._binding = binding

    def unbind(self):
        self.id = None
        self.key = None
        self.rev = None
        self._binding = None

    @property
    def bound(self):
        return (self._binding is not None and
                self.id and self.key and self.rev)

    @classmethod
    def spawn(cls, binding, **data):
        assert '_key' in data
        assert '_id' in data
        assert '_rev' in data
        item = cls(**data)
        item.bind(binding)
        return item

    def delete(self):
        assert self.bound
        self._binding.delete(self.key)
        self.unbind()

    def update(self, **data) -> str:
        assert self.bound
        for key, value in data.items():
            setattr(self, key, value)
        self.rev = self._binding.update(self.key, **data)


class arango_model:

    def __init__(self, collection):
        self.collection = collection

    def __call__(self, model_class):
        model = type(
            f"Arango{model_class.__name__}", (DBModel, model_class), {
                "__collection__": self.collection
            })
        return model
