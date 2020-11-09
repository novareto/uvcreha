from webtest import TestApp


def test_add_user_ok(application):
    import docmanager.auth
    app = TestApp(application)
    ud = dict(username="ck", password="klinger")
    resp = app.post(
        "/user.add", ud,
        expect_errors=True,
    )
    assert resp.status == "201 Created"
    assert resp.json == {"id": "ck"}

    auth = app.app.plugins.get('authentication')
    assert isinstance(auth, docmanager.auth.Auth) is True
    user = auth.from_credentials(ud)
    # assert isinstance(user, docmanager.db.User) is True
    assert user.username == "ck"
    assert user.password == "klinger"

    ud['password'] = u"wrong"
    user = auth.from_credentials(ud)
    assert user is None
