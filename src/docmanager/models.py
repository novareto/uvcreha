from arango.exceptions import DocumentGetError
from pydantic import BaseModel, Field
from .request import Request
from datetime import datetime


class User(BaseModel):
    username: str
    password: str

    @classmethod
    def instanciate(cls, request: Request, userid: str, **bindable):
        connector = request.app.db.connector
        users = connector.collection('users')
        if (userdata := users.get(userid)) is not None:
            return cls(**userdata)
        raise LookupError(f'User {userid} is unknown.')


class Base(BaseModel):
    name: str
    content_type: str 
    mod_date: datetime = Field(default_factory=datetime.utcnow) 
    state: str #ENUM

    @classmethod
    def instanciate(cls, request: Request, docid: str, **bindable):
        connector = request.app.db.connector
        documents = connector.collection('documents')
        if (docdata := documents.get(docid)) is not None:
            return cls(**docdata)
        raise LookupError(f'Document {docid} is unknown.')


class Document(BaseModel):
    body: str

