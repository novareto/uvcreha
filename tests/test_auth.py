from webtest import TestApp as WebApp
import uvcreha.auth


def test_add_user_ok(root, user):
    app = root['/']
    browser = WebApp(app)

    auth = app.utilities.get('authentication')
    assert isinstance(auth, uvcreha.auth.Auth) is True

    ud = dict(uid="123", loginname="test", password="test")
    found = auth.from_credentials(ud)
    assert found['loginname'] == "test"
    assert found['password'] == "test"

    ud['password'] = "wrong"
    found = auth.from_credentials(ud)
    assert found is None

    resp = user.login(browser)
    assert resp.status == "302 Found"
    assert resp.request.environ['test.principal'] is not None
