import abc
import uuid
import arango.exceptions

from datetime import datetime
from typing import Dict, Literal, List, Optional, ClassVar
from roughrider.validation.types import Validatable
from pydantic import BaseModel, Field, ValidationError
from docmanager.app import application
from docmanager.request import Request


class ProtectedModel(abc.ABC):

    __permissions__: List

    @abc.abstractmethod
    def __check_security__(self, request: Request):
        pass


class Model(BaseModel):
    creation_date: datetime = Field(default_factory=datetime.utcnow)
    modification_date: datetime = Field(default_factory=datetime.utcnow)


class ArangoModel:

    __collection__: ClassVar[str]
    __primarykey__: ClassVar[str]

    id: Optional[str]
    key: Optional[str]
    rev: Optional[str]

    @classmethod
    def create(cls, database, **data):
        item = cls(**data)
        data = item.dict(by_alias=True)
        if not data['_key']:
            if cls.__primarykey__:
                item.key = data['_key'] = data[cls.__primarykey__]
            else:
                item.key = data['_key'] = str(uuid.uuid4())
        try:
            with database.transaction(cls.__collection__) as txn:
                collection = txn.collection(cls.__collection__)
                response = collection.insert(data)
                item.id = response["_id"]
                item.key = response["_key"]
                item.rev = response["_rev"]

        except arango.exceptions.DocumentInsertError:
            return None
        return item

    @classmethod
    def find(cls, database, **filters) -> List[Model]:
        collection = database.session.collection(cls.__collection__)
        return [cls(**data) for data in collection.find(filters)]

    @classmethod
    def find_one(cls, database, **filters) -> Optional[Model]:
        collection = database.session.collection(cls.__collection__)
        found = collection.find(filters, limit=1)
        if not found.count():
            return None
        data = found.next()
        return cls(**data)  ### Should we Instanciate it?

    @classmethod
    def exists(cls, database, key) -> bool:
        collection = database.session.collection(cls.__collection__)
        return collection.has({"_key": key})

    @classmethod
    def fetch(cls, database, key) -> Optional[Model]:
        collection = database.session.collection(cls.__collection__)
        if (data := collection.get(key)) is not None:
            return cls(**data)

    @classmethod
    def delete(cls, database, key: str) -> bool:
        try:
            with database.transaction(cls.__collection__) as txn:
                collection = txn.collection(cls.__collection__)
                collection.delete(key)
        except arango.exceptions.DocumentDeleteError:
            return False
        else:
            return True

    def update(self, database) -> bool:
        try:
            with database.transaction(self.__collection__) as txn:
                collection = txn.collection(self.__collection__)
                data = self.dict(by_alias=True)
                data['_id'] = self.id_
                response = collection.replace(data)
                self.key = response["_key"]
                self.rev = response["_rev"]
        except arango.exceptions.DocumentUpdateError:
            return False
        else:
            return True


class RootModel(ArangoModel, Model):

    id: Optional[str] = Field(alias="_id")
    key: Optional[str] = Field(alias="_key")
    rev: Optional[str] = Field(alias="_rev")


@application.models.document(Request)
class Document(RootModel):

    __collection__: str = 'documents'
    __primarykey__: str = ''

    az: str
    username: str
    state: str
    body: str
    content_type: Literal['default'] = 'default'


@application.models.file(Request)
class File(RootModel):

    __collection__: str = 'files'
    __primarykey__: str = 'az'

    az: str
    username: str

    def documents(cls, database, target_model: ArangoModel=Document):
        return target_model.find(database, {
            'username': self.username,
            'az': self.az
        })


@application.models.user(Request)
class User(RootModel):

    __collection__: str = 'users'
    __primarykey__: str = 'username'

    username: str
    password: str
    permissions: Optional[List]

    @property
    def title(self) -> str:
        return self.username

    def files(cls, database, target_model: ArangoModel=File):
        return target_model.find(database, {
            'username': self.username,
        })
