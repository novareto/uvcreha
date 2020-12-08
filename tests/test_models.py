from docmanager.models import Document, User
from typing import Literal


def test_model_crud(connector):

    db_user = User(arangodb.session)
    assert isinstance(db_user, User) is True

    model = db_user.model(
        username="souheil", password="secret", email="trollfot@gmail.com")
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
