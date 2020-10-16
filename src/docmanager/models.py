from arango.exceptions import DocumentGetError
from pydantic import BaseModel
from .request import Request


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


class Document(BaseModel):
    body: str

    @classmethod
    def instanciate(cls, request: Request, docid: str, **bindable):
        connector = request.app.db.connector
        documents = connector.collection('documents')
        if (docdata := documents.get(docid)) is not None:
            return cls(**docdata)
        raise LookupError(f'Document {docid} is unknown.')
