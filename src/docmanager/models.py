import enum
from typing import List, Optional, Any, ClassVar
from datetime import datetime, date
from pydantic import BaseModel, Field, SecretStr, EmailStr, validator
from reiter.arango.model import ArangoModel
from reiter.application.registries import NamedComponents


class Message(BaseModel):
    type: str
    body: str


class Model(ArangoModel):
    creation_date: datetime = Field(default_factory=datetime.utcnow)


class Document(Model):

    __collection__ = "documents"

    az: str
    username: str
    state: str
    content_type: str = None
    state: Optional[str] = None
    item: Optional[Any]

    alternatives: ClassVar[Any] = NamedComponents()

    @validator('item', always=True, pre=True)
    def set_item(cls, v, values):
        if v:
            model_class = cls.alternatives.get(values['content_type'])
            if model_class is None:
                raise KeyError(
                    f'Unknown document type: {values["content_type"]}.')
            return model_class(**v)


class File(Model):

    __collection__ = "files"

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
    name: Optional[str] = Field(
        title="Vorname",
        description="Vorname"
    )

    surname: Optional[str] = Field(
        title="Nachname",
        description="Nachname"
    )

    birthdate: Optional[date] = Field(
        title="Geburtsdatum"
    )

    datenschutz: Optional[bool] = Field(
        title="Datenschutz",
        default=False
    )

    mobile: Optional[str] = Field(
        title="Telefonnummer",
        description="Telefonnummer"
    )

    messaging_type: MessagingType = MessagingType.email
    webpush_subscription: Optional[str] = ""
    webpush_activated: Optional[bool] = False


class User(Model):

    __collection__ = "users"

    username: str = Field(
        title="Loginname", description="Bitte geb hier was ein.")

    password: SecretStr = Field(
        title="Passwort", description="Bitte geb das PW ein.")

    email: Optional[EmailStr] = Field(
        title="E-Mail", description="Bitte geben Sie die E-Mail ein")

    state: Optional[str] = None
    permissions: Optional[List] = ['document.view']
    preferences: Optional[UserPreferences]

    @property
    def __key__(self) -> str:
        return self.username
