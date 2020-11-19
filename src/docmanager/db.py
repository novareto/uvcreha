import abc
import pydantic.types
from collections import namedtuple
from contextlib import ContextDecorator
from typing import Iterable, List, Optional, ClassVar

import orjson
import arango

import horseman.http
from docmanager import models, registries
from docmanager.validation import catch_pydantic_exception


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


class DBModel(abc.ABC):

    parents: Iterable['DBModel']

    @abc.abstractmethod
    def model(self, **kwargs):
        pass

    @abc.abstractmethod
    def create(self, **data):
        pass

    @abc.abstractmethod
    def find(self, **filters) -> List[models.Model]:
        pass

    @abc.abstractmethod
    def find_one(self, **filters) -> Optional[models.Model]:
        pass

    @abc.abstractmethod
    def fetch(self, key) -> Optional[models.Model]:
        pass

    @abc.abstractmethod
    def exists(self, key) -> bool:
        pass

    @abc.abstractmethod
    def delete(self, key) -> bool:
        pass

    @abc.abstractmethod
    def update(self, item) -> bool:
        pass


class ArangoModel(DBModel):

    __collection__: ClassVar[str]
    __primarykey__: ClassVar[str]
    __parents__: ClassVar[List[DBModel]]

    def __init__(self, database: Database):
        self.session = database

    def model(self, **kwargs):
        return None

    def parents(self, **kwargs):
        for parent in self.__parents__:
            yield parent.find_one(**kwargs)

    @catch_pydantic_exception
    def create(self, **data):

        # check parents existance.
        for parent in self.__parents__:
            collection = self.session.collection(parent.__collection__)
            if not collection.has({"_key": data[parent.__primarykey__]}):
                raise horseman.http.HTTPError(404)

        item = self.model(**data)
        data = item.dict()
        try:
            with Transaction(self.session, self.__collection__) as txn:
                collection = txn.collection(self.__collection__)
                response = collection.insert(data)
                item.id = response["_id"]
                item.key = response["_key"]
                item.rev = response["_rev"]
        except arango.exceptions.DocumentInsertError as exc:
            raise horseman.http.HTTPError(exc.http_code, exc.message)
        return item

    @catch_pydantic_exception
    def find(self, **filters) -> List[models.Model]:
        collection = self.session.collection(self.__collection__)
        return [self.model(**data) for data in collection.find(filters)]

    @catch_pydantic_exception
    def find_one(self, **filters) -> Optional[models.Model]:
        collection = self.session.collection(self.__collection__)
        found = collection.find(filters, limit=1)
        if not found.count():
            return None
        data = found.next()
        return self.model(**data)

    @catch_pydantic_exception
    def fetch(self, key) -> Optional[models.Model]:
        collection = self.session.collection(self.__collection__)
        if (data := collection.get(key)) is not None:
            return self.model(**data)

    def exists(self, key) -> bool:
        collection = self.session.collection(self.__collection__)
        return collection.has({"_key": key})

    def delete(self, key) -> bool:
        try:
            with Transaction(self.session, self.__collection__) as txn:
                collection = txn.collection(self.__collection__)
                collection.delete(key)
        except arango.exceptions.DocumentDeleteError as exc:
            raise horseman.http.HTTPError(exc.http_code, exc.message)
        return True

    def update(self, item) -> bool:
        try:
            with Transaction(self.session, self.__collection__) as txn:
                collection = txn.collection(self.__collection__)
                data = item.dict()
                response = collection.replace(data)
                item.rev = response["_rev"]
        except arango.exceptions.DocumentUpdateError as exc:
            raise horseman.http.HTTPError(exc.http_code, exc.message)
        return True


class User(ArangoModel):
    model = models.User

    __collection__: str = 'users'
    __primarykey__: str = 'username'
    __parents__: List = []

    def files(self, **filters):
        return File(self.session).find(**filters)


class File(ArangoModel):
    model = models.File

    __collection__: str = 'files'
    __primarykey__: str = 'az'
    __parents__: List = [User]

    def documents(self, **filters):
        return Document(self.session).find(**filters)


class Document(ArangoModel):

    __collection__: str = 'documents'
    __primarykey__: str = ''
    __parents__: List = [File, User]

    alternatives = registries.NamedComponents()

    def model(self, content_type, **kwargs) -> Optional[models.Model]:
        model_class = self.alternatives.get(content_type)
        if model_class is None:
            raise horseman.http.HTTPError(
                400, f'Unknown content_type: {content_type}')
        return model_class(content_type=content_type, **kwargs)
