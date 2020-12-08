import enum
from typing import List, Optional
from datetime import datetime, date
from pydantic import BaseModel, Field, SecretStr, EmailStr
from reiter.arango.model import arango_model, PluggableModel
from docmanager.registries import NamedComponents


class Message(BaseModel):
    type: str
    body: str


class Model(BaseModel):
    creation_date: datetime = Field(default_factory=datetime.utcnow)


@arango_model('docs')
class BaseDocument(BaseModel):
    az: str
    username: str
    state: str
    content_type: str
    state: Optional[str] = None


class Document(PluggableModel):

    __collection__ = BaseDocument.__collection__
    alternatives = NamedComponents()

    @classmethod
    def lookup(cls, content_type: str, **data):
        model_class = cls.alternatives.get(content_type)
        if model_class is None:
            raise KeyError(f'Unknown document type: {content_type}.')
        return model_class


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
    name: str = Field(title="Vorname", description="Vorname")
    surname: str = Field(title="Nachname", description="Nachname")
    birthdate: Optional[date] = Field(title="Geburtsdatum")
    webpush_subscription: Optional[str] = ""
    webpush_activated: Optional[bool] = False
    datenschutz: Optional[bool] = Field(title="Datenschutz", default=False)


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
    preferences: Optional[UserPreferences]  #  = Field(default_factory=UserPreferences)

    webpush_subscription: Optional[str] = ""
    webpush_activated: Optional[bool] = False

    @property
    def __key__(self) -> str:
        return self.username

    def get_files(self, request, key):
        binding_file = request.database.bind(File)
        return binding_file.find(username=key)

    def get_documents(self, request, username, az):
        binding_doc = request.database.bind(Document)
        return binding_doc.find(username=username, az=az)
