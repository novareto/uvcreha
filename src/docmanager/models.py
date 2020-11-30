import enum
import uuid
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field, SecretStr, EmailStr


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


class MessagingType(str, enum.Enum):
    """Messaging system choices.
    """
    email = 'email'
    webpush = 'webpush'


class UserPreferences(BaseModel):
    """User-based application preferences
    """
    messaging_type: MessagingType = MessagingType.email


class User(Model):

    username: str = Field(
        title="Loginname", description="Bitte geb hier was ein.")

    password: SecretStr = Field(
        title="Passwort", description="Bitte geb das PW ein.")

    email: Optional[EmailStr] = Field(
        title="E-Mail", description="Bitte geben Sie die E-Mail ein")

    permissions: Optional[List] = ['document.view']
    preferences: UserPreferences = Field(default_factory=UserPreferences)

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
