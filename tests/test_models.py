import hamcrest
from typing import Literal
from uvcreha.models import Document, User


def test_model_crud(db_connector):

    db = db_connector.get_database()
    wrapper = db(User)
    model = wrapper.model(
        uid="123456",
        loginname="souheil",
        password="secret",
        email="trollfot@gmail.com"
    )
    assert isinstance(model, User) is True
    assert model.loginname == "souheil"
    assert model.password.get_secret_value() == "secret"

    saved_user, response = wrapper.create(**model.dict())
    assert saved_user.key == '123456'
    assert wrapper.exists('123456') is True

    assert isinstance(saved_user, User) is True
    saved_user.password = "newpw"

    response = db.save(saved_user)
    hamcrest.assert_that(response, hamcrest.has_entries({
        '_id': 'users/123456',
        '_key': '123456',
        '_rev': hamcrest.instance_of(str),
        '_old_rev': hamcrest.instance_of(str)
    }))

    new_user = wrapper.fetch(saved_user.key)
    assert new_user.password.get_secret_value() == "newpw"
