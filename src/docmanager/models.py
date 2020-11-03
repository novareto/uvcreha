import abc
import uuid
import arango.exceptions

from datetime import datetime
from typing import Dict, List, Optional, ClassVar
from roughrider.validation.types import Validatable
from pydantic import BaseModel, Field, ValidationError
from docmanager.app import application
from docmanager.request import Request


class ProtectedModel(abc.ABC):

    __permissions__: List

    @abc.abstractmethod
    def __check_security__(self, request: Request):
        pass


class RootModel(BaseModel):

    __collection__: ClassVar[str]
    __primarykey__: ClassVar[str] = ''

    id_: Optional[str] = Field(alias="_id")
    key_: Optional[str] = Field(alias="_key")
    rev_: Optional[str] = Field(alias="_rev")

    @classmethod
    def create(cls, database, data: dict):
        item = cls(**data)
        data = item.dict(by_alias=True)
        if not data['_key']:
            if cls.__primarykey__:
                item.key_ = data['_key'] = data[cls.__primarykey__]
            else:
                item.key_ = data['_key'] = str(uuid.uuid4())
        try:
            with database.transaction(cls.__collection__) as txn:
                collection = txn.collection(cls.__collection__)
                response = collection.insert(data)
                item.id_ = response["_id"]
                item.key_ = response["_key"]
                item.rev_ = response["_rev"]

        except arango.exceptions.DocumentInsertError:
            return None
        return item

    @classmethod
    def fetch(cls, database, key):
        collection = database.session.collection(cls.__collection__)
        if (data := collection.get(key)) is not None:
            return cls(**data)

    @classmethod
    def delete(cls, database, key: str):
        try:
            with database.transaction(cls.__collection__) as txn:
                collection = txn.collection(cls.__collection__)
                collection.delete(key)
        except arango.exceptions.DocumentDeleteError:
            return False
        else:
            return True

    def update(self, database):
        try:
            with database.transaction(self.__collection__) as txn:
                collection = txn.collection(self.__collection__)
                data = self.dict(by_alias=True)
                data['_id'] = self.id_
                response = collection.replace(data)
                self.key_ = response["_key"]
                self.rev_ = response["_rev"]
        except arango.exceptions.DocumentUpdateError:
            return False
        else:
            return True


class Content(BaseModel):
    creation_date: datetime = Field(default_factory=datetime.utcnow)
    modification_date: datetime = Field(default_factory=datetime.utcnow)


@application.models.component('document')
class Document(Content):
    id: Optional[str] = Field(default_factory=uuid.uuid4)
    state: str
    content_type: str
    body: str

    @property
    def key(self):
        return self.id


@application.models.component('file')
class File(Content):
    az: str
    documents: Dict[str, Dict] = Field(default_factory=dict)

    @property
    def key(self):
        return self.az


@application.models.component('user')
class User(RootModel):

    __collection__ = 'users'
    __primarykey__ = 'username'

    username: str
    password: str
    permissions: Optional[List]
    files: Dict[str, File] = Field(default_factory=dict)
