
def test_add_user(api_app):
    from webtest import TestApp

    app = TestApp(api_app)
    resp = app.post_json(
        "/user.add",
        {"nothing": "at_all"},
        expect_errors=True,
    )
    assert resp.json == {
        "errors": [
            {   'loc': ['uid'],
                'msg': 'field required',
                'type': 'value_error.missing',
            },
            {
                "loc": ["loginname"],
                "msg": "field required",
                "type": "value_error.missing",
            },
            {
                "loc": ["password"],
                "msg": "field required",
                "type": "value_error.missing",
            },
        ],
        "name": "uvcreha.models.User",
        "type": "Model validation",
    }


def test_add_user_ok(api_app):
    from webtest import TestApp

    app = TestApp(api_app)
    resp = app.post_json(
        "/user.add",
        dict(uid="12345", loginname="cklinger", password="klinger"),
        expect_errors=True,
    )
    assert resp.status == "201 Created"
    assert resp.json == {"id": "12345"}

    resp = app.get("/users/12345")
    assert resp.status == "200 OK"
    assert resp.json["_key"] == "12345"


def test_add_folder(api_app, user):
    from webtest import TestApp

    app = TestApp(api_app)
    resp = app.put_json(
        f"/users/{user.user.uid}/file.add", {
            'az': "4711",
            'mnr': "232",
            'vid': "33",
        }
    )
    assert resp.status == "201 Created"
    assert resp.json["az"] == "4711"

    resp = app.get(f"/users/{user.user.uid}/files/4711")
    assert resp.status == "200 OK"
    assert resp.json["az"] == "4711"


def test_add_file(api_app, user):
    from webtest import TestApp
    from pydantic import BaseModel
    from uvcreha.models import Document
    from typing import Literal


    @Document.alternatives.component('event')
    class Event(BaseModel):
        myfield: str


    app = TestApp(api_app)

    resp = app.put_json(
        f"/users/{user.user.uid}/file.add", {
            'az': "1234",
            'mnr': '3223',
            'vid': '23',
        }
    )
    assert resp.status == "201 Created"

    resp = app.put_json(
        f"/users/{user.user.uid}/files/1234/doc.add", {
            'body': "Some Doc",
            'myfield': "",
            'content_type': "event"
        }
    )
    assert resp.status == "201 Created"
    assert resp.json['az'] == "1234"

    Document.alternatives.unregister('event')
