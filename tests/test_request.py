from uvcreha.request import Request
from arango.database import StandardDatabase


def test_query(uvcreha, environ, json_post_environ):

    request = Request(uvcreha, environ, None)
    assert request.query == {}

    request = Request(uvcreha, json_post_environ, None)
    assert request.query == {"action": ["login"], "token": ["abcdef"]}


def test_user(uvcreha, environ, environ_with_user):

    request = Request(uvcreha, environ, None)
    assert request.user is None

    request = Request(uvcreha, environ_with_user, None)
    assert request.user == {"id": "SomeUser"}


def test_db(uvcreha, environ):
    request = Request(uvcreha, environ, None)
    assert request._db is None
    db = request.database
    assert request._db is not None
    assert request._db is db
    assert isinstance(db, StandardDatabase)
    assert db.name == "tests"
