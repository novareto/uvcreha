import abc
import uuid
import arango.exceptions

from datetime import datetime
from typing import List, Optional, ClassVar
from roughrider.validation.types import Validatable
from pydantic import BaseModel, Field
from docmanager.app import application
from docmanager.request import Request


class ProtectedModel(abc.ABC):

    __permissions__: List

    @abc.abstractmethod
    def __check_security__(self, request: Request):
        pass


class Model(BaseModel):

    __collection__: ClassVar[str]
    __primarykey__: ClassVar[str]

    key_: Optional[str] = Field(alias="_key")
    rev_: Optional[str] = Field(alias="_rev")

    @classmethod
    def save(cls, database, **data):
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
                ret = collection.insert(data)
        except arango.exceptions.DocumentInsertError:
            return None
        return item

    @classmethod
    def fetch(cls, database, key):
        collection = database.session.collection(cls.__collection__)
        if (data := collection.get(key)) is not None:
            return cls(**data)

    @classmethod
    def delete(cls, database, key):
        try:
            with database.transaction(cls.__collection__) as txn:
                collection = txn.collection(cls.__collection__)
                collection.delete(key)
        except arango.exceptions.DocumentDeleteError:
            return False
        else:
            return True


class Content(Model):
    name: str
    state: str
    content_type: str
    creation_date: datetime = Field(default_factory=datetime.utcnow)
    modification_date: datetime = Field(default_factory=datetime.utcnow)


@application.models.component('document')
class Document(Content):

    __collection__ = 'documents'
    __primarykey__ = ''

    body: str


@application.models.component('file')
class File(Content):

    __collection__ = 'files'
    __primarykey__ = 'az'

    az: str
    documents: List[Document] = Field(default_factory=list)


@application.models.component('user')
class User(Model):

    __collection__ = 'users'
    __primarykey__ = 'username'

    username: str
    password: str
    permissions: Optional[List]

    files: List[File] = Field(default_factory=list)
