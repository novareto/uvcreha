from webtest import TestApp


def test_model(application):
    from docmanager.models import Document as BaseDoc
    from docmanager.db import Document

    @Document.alternatives.component("base")
    class BaseDoc(BaseDoc):
        pass

    app = TestApp(application)
    doc = Document(app.app.database.session)
    assert isinstance(doc, Document) is True
    instance = doc.model(
        content_type="base", az="2", username="4711", body="", state=""
    )
    assert isinstance(instance, BaseDoc) is True
    Document.alternatives.unregister("base")


def test_model_alternative(application):
    from docmanager.models import Document as BaseDoc
    from docmanager.db import Document
    from typing import Literal

    @Document.alternatives.component("event")
    class Event(BaseDoc):
        content_type: Literal["event"]
        myfield: str

    app = TestApp(application)
    doc = Document(app.app.database.session)
    assert isinstance(doc, Document) is True
    instance = doc.model(
        "event", az="2", username="4711", body="", myfield="", state=""
    )
    assert isinstance(instance, Event) is True
    Document.alternatives.unregister("event")


def test_model_crud(application):
    from docmanager.models import User as _User
    from docmanager.db import User

    app = TestApp(application)
    db_user = User(app.app.database.session)
    assert isinstance(db_user, User) is True

    model = db_user.model(username="souheil", password="secret")
    assert isinstance(model, _User) is True
    assert model.username == "souheil"
    assert model.password.get_secret_value() == "secret"

    saved_user = db_user.create(**model.dict())
    assert saved_user.key == 'souheil'
    assert db_user.exists('souheil') is True

    assert isinstance(saved_user, _User) is True
    saved_user.password = "newpw"

    assert db_user.update(saved_user) is True

    new_user = db_user.fetch(saved_user.key)
    assert new_user.password.get_secret_value() == "newpw"
    

