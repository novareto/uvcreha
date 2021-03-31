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
    date: datetime
    actions: Dict[str, str]


class Link(NamedTuple):
    title: str
    url: str
    css: str = ''


class Message(BaseModel):
    type: str
    body: str


class Model(ArangoModel):
    creation_date: datetime = Field(default_factory=datetime.utcnow)


class Document(Model):

    __collection__ = "documents"

    docid: str = Field(
        title="DocumentID",
        description="Eindeutige ID des Dokuments"
    )

    az: str = Field(
        title="Aktenzeichen",
        description="Eindeutige ID der Akte"
    )

    uid: str = Field(
        title="UID Versicherter",
        description="Eindeutige ID des Versicherten"
    )
    state: str = document_workflow.default_state.name
    content_type: str = Field(
        title="Dokumentart",
        description="Bitte wählen Sie eine Dokumentart",
        default=None
    )

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

    uid: str = Field(title="UID", description="Interne ID des Benutzers")
    az: str = Field(title="Aktenzeichen", description="Aktenzeichen des entsprechenden Falls")
    mnr: str = Field(title="Mitgliedsnummer", description="Mitgliedsnummer des Unternehmens")
    vid: str = Field(title="Versichertenfall ID", description="ID des Versichertenfalls")
    state: str = file_workflow.default_state.name

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
        description="Bitte bestätigen Sie hier, dass Sie die Ausführungen zum Datenschutz\
                gelesen und akzeptiert haben.",
        default=False
    )

    teilnahme: Optional[bool] = Field(
        title="Teilnahme",
        description="Bitte bestätigen Sie uns hier die Teilnahme am Online-Verfahren.",
        default=False
    )

    mobile: Optional[str] = Field(
        title="Telefonnummer",
        description="Telefonnummer"
    )

    messaging_type: Optional[List[MessagingType]] = Field(
        default=[MessagingType.email],
        title="Benachrichtigungen",
        description="Bitte wählen Sie eine/oder mehrere Arten der Benachrichtiung aus"
    )
    webpush_subscription: Optional[str] = ""
    webpush_activated: Optional[bool] = False


class User(Model):

    __collection__ = "users"

    uid: str = Field(
        title=u"ID", description="Internal User ID")

    loginname: str = Field(
        title="Loginname", description="Bitte tragen Sie hier den Loginnamen ein.")

    password: SecretStr = Field(
        title="Passwort", description="Bitte tragen Sie hier das Kennwort ein.")

    email: Optional[EmailStr] = Field(
        title="E-Mail", description="Bitte geben Sie die E-Mail ein")

    state: str = user_workflow.default_state.name
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
            date=obj.creation_date,
            title=obj.loginname,
            state=wf.state,
            link=request.route_path('user.view', uid=obj.uid),
            actions=(
                Link(title='Bearbeiten',
                     url=request.route_path(
                         'user.edit', uid=obj.uid),
                     css='fa fa-edit'),
                Link(title='Akte anlegen',
                     url=request.route_path(
                         'user.new_file', uid=obj.uid),
                     css='fa fa-folder'),
            )
        )


class FileBrain(Brain):

    @classmethod
    def create(cls, obj, request):
        wf = file_workflow(obj)
        return cls(
            id=obj.__key__,
            date=obj.creation_date,
            title=f"File {obj.az} ({obj.mnr})",
            state=wf.state,
            link=request.route_path('file.view', uid=obj.uid, az=obj.az),
            actions=(
                Link(title="Bearbeiten",
                     url=request.route_path(
                         'file.edit', uid=obj.uid, az=obj.az),
                     css='fa fa-edit'),
                Link(title='Dokument anlegen',
                     url=request.route_path(
                         'file.new_doc', uid=obj.uid, az=obj.az),
                     css='fa fa-file'),
            )
        )


class DocBrain(Brain):

    @classmethod
    def create(cls, obj, request):
        wf = document_workflow(obj)
        return cls(
            id=obj.__key__,
            date=obj.creation_date,
            title=f"Document {obj.az} ({obj.content_type})",
            state=wf.state,
            link=request.route_path(
                'doc.view', uid=obj.uid, az=obj.az, docid=obj.docid),
            actions=(
                Link(title='Bearbeiten',
                    url=request.route_path(
                        'doc.edit',
                        uid=obj.uid, az=obj.az, docid=obj.docid),
                    css='fa fa-edit'),
            )
        )
