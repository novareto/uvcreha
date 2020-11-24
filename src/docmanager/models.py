import abc
import uuid
import orjson
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field, SecretStr
from docmanager.request import Request


class Model(BaseModel):

    id: Optional[str] = Field(alias="_id")
    key: Optional[str] = Field(alias="_key")
    rev: Optional[str] = Field(alias="_rev")

    creation_date: datetime = Field(default_factory=datetime.utcnow)


class Document(Model):

    az: str
    username: str
    state: str
    body: str
    content_type: str

    def dict(self, by_alias=True, **kwargs):
        if not self.key:
            self.key = str(uuid.uuid4())
        return super().dict(by_alias=by_alias, **kwargs)

    @property
    def url(self):
        return f"/users/{self.username}/files/{self.az}/documents/{self.key}"


class File(Model):

    az: str
    username: str

    def dict(self, by_alias=True, **kwargs):
        if not self.key:
            self.key = self.az
        return super().dict(by_alias=by_alias, **kwargs)

    @property
    def url(self):
        return f"/users/{self.username}/files/{self.az}"


class User(Model):

    username: str = Field(
        title="Loginname", description="Bitte geb hier was ein.")
    password: SecretStr = Field(
        title="Passwort", description="Bitte geb das PW ein.")
    permissions: Optional[List] = ['document.view']

    webpush_subscription: Optional[str] = ""
    webpush_activated: Optional[bool] = False

    @property
    def title(self) -> str:
        return self.username

    @property
    def url(self):
        return f"/users/{self.username}"

    def dict(self, by_alias=True, **kwargs):
        if not self.key:
            self.key = self.username
        return super().dict(by_alias=by_alias, **kwargs)

    def json(self, by_alias=True, **kwargs):
        return super().json(by_alias=by_alias, **kwargs)


class Message(BaseModel):
    type: str
    body: str
