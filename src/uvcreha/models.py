import enum
from typing import Dict, List, Optional, Any, ClassVar, NamedTuple
from datetime import datetime, date
from pydantic import BaseModel, Field, SecretStr, EmailStr, validator
from reiter.arango.model import ArangoModel
from reiter.application.registries import NamedComponents
from uv.models.models import Unternehmen, VersichertenFall
from uvcreha.workflow import user_workflow, document_workflow, file_workflow


class Brain(NamedTuple):
    id: str
    state: str
    title: str
    link: str
    actions: Dict[str, str]


class Message(BaseModel):
    type: str
    body: str


class Model(ArangoModel):
    creation_date: datetime = Field(default_factory=datetime.utcnow)


class Document(Model):

    __collection__ = "documents"

    docid: str
    az: str
    uid: str
    state: str
    content_type: str = None
    state: Optional[str] = None
    item: Optional[Any]

    alternatives: ClassVar[Any] = NamedComponents()

    @property
    def __key__(self):
        return self.docid

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

    az: str = Field(title="Aktenzeigen")
    uid: str = Field(title="UID")
    mnr: str = Field(title="Mitgliedsnummer")
    vid: str = Field(title="VersichertenfallID")
    state: Optional[str] = None

    unternehmen: Optional[Unternehmen]
    versichertenfall: Optional[VersichertenFall]

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

    uid: str = Field(
        title=u"ID", description="Internal User ID")

    loginname: str = Field(
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
        return self.uid


class UserBrain(Brain):

    @classmethod
    def create(cls, obj, request):
        wf = user_workflow(obj)
        return cls(
            id=obj.__key__,
            title=obj.loginname,
            state=wf.state,
            link=request.route_path('user.view', uid=obj.uid),
            actions={
                'Edit': request.route_path(
                    'user.edit', uid=obj.uid),
                'New file': request.route_path(
                    'user.new_file', uid=obj.uid)
            }
        )


class FileBrain(Brain):

    @classmethod
    def create(cls, obj, request):
        wf = file_workflow(obj)
        return cls(
            id=obj.__key__,
            title=f"File {obj.az} ({obj.mnr})",
            state=wf.state,
            link=request.route_path('file.view', uid=obj.uid, az=obj.az),
            actions={
                'Edit': request.route_path(
                    'file.edit', uid=obj.uid, az=obj.az),
                'New document': request.route_path(
                    'file.new_doc', uid=obj.uid, az=obj.az)
            }
        )


class DocBrain(Brain):

    @classmethod
    def create(cls, obj, request):
        wf = document_workflow(obj)
        return cls(
            id=obj.__key__,
            title=f"Document {obj.az} ({obj.content_type})",
            state=wf.state,
            link=request.route_path(
                'doc.view', uid=obj.uid, az=obj.az, docid=obj.docid),
            actions={
                'Edit': request.route_path(
                    'doc.edit', uid=obj.uid, az=obj.az, docid=obj.docid),
            }
        )
