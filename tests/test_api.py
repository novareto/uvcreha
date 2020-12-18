
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
            {
                "loc": ["username"],
                "msg": "field required",
                "type": "value_error.missing",
            },
            {
                "loc": ["password"],
                "msg": "field required",
                "type": "value_error.missing",
            },
        ],
        "name": "docmanager.models.User",
        "type": "Model validation",
    }


def test_add_user_ok(api_app):
    from webtest import TestApp

    app = TestApp(api_app)
    resp = app.post_json(
        "/user.add",
        dict(username="cklinger", password="klinger"),
        expect_errors=True,
    )
    assert resp.status == "201 Created"
    assert resp.json == {"id": "cklinger"}

    resp = app.get("/users/cklinger")
    assert resp.status == "200 OK"
    assert resp.json["_key"] == "cklinger"


def test_add_folder(api_app, user):
    from webtest import TestApp

    app = TestApp(api_app)
    resp = app.put_json(
        f"/users/{user.user.username}/file.add", {
            'az': "4711"
        }
    )
    assert resp.status == "201 Created"
    assert resp.json["az"] == "4711"

    resp = app.get(f"/users/{user.user.username}/files/4711")
    assert resp.status == "200 OK"
    assert resp.json["az"] == "4711"


def test_add_file(api_app, user):
    from webtest import TestApp
    from pydantic import BaseModel
    from docmanager.models import Document
    from typing import Literal


    @Document.alternatives.component('event')
    class Event(BaseModel):
        myfield: str


    app = TestApp(api_app)

    resp = app.put_json(
        f"/users/{user.user.username}/file.add", {
            'az': "1234"
        }
    )
    assert resp.status == "201 Created"

    resp = app.put_json(
        f"/users/{user.user.username}/files/1234/doc.add", {
            'body': "Some Doc",
            'myfield': "",
            'content_type': "event"
        }
    )
    assert resp.status == "201 Created"
    assert resp.json['az'] == "1234"

    Document.alternatives.unregister('event')
