import enum
import uuid
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field, SecretStr, EmailStr
from reiter.arango.model import arango_model


class Message(BaseModel):
    type: str
    body: str


class Model(BaseModel):
    creation_date: datetime = Field(default_factory=datetime.utcnow)


@arango_model('docs')
class Document(Model):
    az: str
    username: str
    state: str
    content_type: str
    state: Optional[str] = None


@arango_model('files')
class File(Model):

    az: str
    username: str

    @property
    def __key__(self):
        return self.az


class MessagingType(str, enum.Enum):
    """Messaging system choices.
    """
    email = 'email'
    webpush = 'webpush'


class UserPreferences(BaseModel):
    """User-based application preferences
    """
    messaging_type: MessagingType = MessagingType.email


@arango_model('users')
class User(Model):

    username: str = Field(
        title="Loginname", description="Bitte geb hier was ein.")

    password: SecretStr = Field(
        title="Passwort", description="Bitte geb das PW ein.")

    email: Optional[EmailStr] = Field(
        title="E-Mail", description="Bitte geben Sie die E-Mail ein")

    state: Optional[str] = None
    permissions: Optional[List] = ['document.view']
    preferences: UserPreferences = Field(default_factory=UserPreferences)

    webpush_subscription: Optional[str] = ""
    webpush_activated: Optional[bool] = False

    @property
    def __key__(self) -> str:
        return self.username
