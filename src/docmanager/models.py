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
        userdata = users.get(userid)
        return cls(**userdata)
