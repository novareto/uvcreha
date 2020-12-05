import pytest
from docmanager.database import Database
from docmanager.models import User


def test_API():
    database = Database(
        user='root',
        password='palotida56',
        database='adhoc'
    )


    user = database.query(User).fetch('hans')
    hans = database.query(User).find_one(email="test@test.com")


    new_user = User(
        username='my_new_user',
        password='Some password'
    )

    with pytest.raises(AssertionError):
        new_user.update(email="some@email.com")

    database.query(User).add(new_user)
    new_user.update(email="some@email.com")

    new_user.delete()
    assert not new_user.bound
    assert new_user.key is None
