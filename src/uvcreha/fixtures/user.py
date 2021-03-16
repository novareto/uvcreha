import pytest
from uvcreha.models import User
from uvcreha.workflow import user_workflow


class TestUser:

    def __init__(self, user):
        self.user = user

    def login(self, app):
        response = app.post("/login", {
            'loginname': self.user.loginname,
            'password': self.user.password.get_secret_value(),
            'form.trigger': 'trigger.speichern',
        })
        return response


@pytest.fixture(scope="session")
def user(web_app):

    # Add the User
    user = User(
        uid='123',
        loginname='test',
        password='test',
        permissions=['document.view', 'document.add']
    )
    db = web_app.connector.get_database()
    db.add(user)
    yield TestUser(user)
    db.delete(user)


@pytest.fixture(scope="session")
def reg_user(web_app):

    # Add the User
    user = User(
        uid='123',
        loginname='test',
        password='test',
        state=user_workflow.states.active.name,
        permissions=['document.view', 'document.add']
    )
    db = web_app.connector.get_database()
    db.add(user)
    yield TestUser(user)
    db.delete(user)

