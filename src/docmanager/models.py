import abc
from typing import Union, Optional
from datetime import datetime
from pkg_resources import iter_entry_points

from arango.exceptions import DocumentGetError
from pydantic import BaseModel, Field

from docmanager.request import Request
from docmanager import logger


class ProtectedModel(abc.ABC):

    __permissions__: list

    @abc.abstractmethod
    def __check_security__(self, request: Request):
        pass



class Model(BaseModel, abc.ABC):

    key_: Optional[str] = Field(alias="_key")
    rev_: Optional[str] = Field(alias="_rev")

    @property
    def id_(self) -> Optional[str]:
        if self.key_ is None:
            return None
        return f"{self.__collection__}/{self.key_}"

    def data(self) -> dict:
        data = self.dict(by_alias=True)
        data["_id"] = self.id_
        return data


class Relation(Model):

    __edge__: str = None

    from_: Union[str, Model] = Field(alias="_from")
    to_: Union[str, Model] = Field(alias="_to")


class Document(Model):

    __collection__: str = None

    name: str
    state: str # ENUM
    content_type: str
    modification_date: datetime = Field(default_factory=datetime.utcnow)

    @classmethod
    def instanciate(cls, request: Request, key: str, **bindable):
        connector = request.app.db.connector
        documents = connector.collection(cls.__collection__)
        if (data := documents.get(key)) is not None:
            return cls(**data)
        raise LookupError(
            f'Document {cls.__collection__}/{key} is unknown.')


class File(Document):

    __collection__ = 'files'

    az: str
    creation_date: datetime = Field(default_factory=datetime.utcnow)


class User(Document):
    __collection__ = 'users'

    username: str
    password: str
    permissions: set = {'document.view'}


class Document(Document):
    __collection__ = 'documents'

    body: str
