from docmanager.models import Document as BaseDoc, User as BaseUser
from docmanager.db import Document, User
from typing import Literal


def test_model(arangodb):

    @Document.alternatives.component("doc")
    class Doc(BaseDoc):
        pass

    doc = Document(arangodb.session)
    assert isinstance(doc, Document) is True
    instance = doc.model(
        content_type="doc",
        az="2",
        username="4711",
        body="",
        state=""
    )
    assert isinstance(instance, BaseDoc) is True
    Document.alternatives.unregister("doc")


def test_model_alternative(arangodb):

    @Document.alternatives.component("event")
    class Event(BaseDoc):
        content_type: Literal["event"]
        myfield: str

    doc = Document(arangodb.session)
    assert isinstance(doc, Document) is True
    instance = doc.model(
        "event",
        az="2",
        username="4711",
        body="",
        myfield="",
        state=""
    )
    assert isinstance(instance, Event) is True
    Document.alternatives.unregister("event")


def test_model_crud(arangodb):

    db_user = User(arangodb.session)
    assert isinstance(db_user, User) is True

    model = db_user.model(username="souheil", password="secret")
    assert isinstance(model, BaseUser) is True
    assert model.username == "souheil"
    assert model.password.get_secret_value() == "secret"

    saved_user = db_user.create(**model.dict())
    assert saved_user.key == 'souheil'
    assert db_user.exists('souheil') is True

    assert isinstance(saved_user, BaseUser) is True
    saved_user.password = "newpw"

    assert db_user.replace(saved_user) is True

    new_user = db_user.fetch(saved_user.key)
    assert new_user.password.get_secret_value() == "newpw"
