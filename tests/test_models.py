import hamcrest
from typing import Literal
from uvcreha.contenttypes import registry


def test_model_crud(arangodb):

    user_type = registry['user']

    db = arangodb.get_database()

    wrapper = user_type.bind(db)
    model = user_type.factory(
        uid="123456",
        loginname="souheil",
        password="secret",
        email="trollfot@gmail.com"
    )
    assert model['loginname'] == "souheil"
    assert model['password'] == "secret"

    saved_user, response = wrapper.create(_key=model.id, **model)
    assert wrapper.exists('123456') is True

    assert isinstance(saved_user, user_type.factory) is True
    saved_user['password'] = "newpw"

    response = wrapper.update(**saved_user)
    hamcrest.assert_that(response, hamcrest.has_entries({
        '_id': 'users/123456',
        '_key': '123456',
        '_rev': hamcrest.instance_of(str),
        '_old_rev': hamcrest.instance_of(str)
    }))

    new_user = wrapper.fetch(saved_user.id)
    assert new_user['password'] == "newpw"
