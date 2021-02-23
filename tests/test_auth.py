from webtest import TestApp
import uvcreha.auth


def test_add_user_ok(api_app, web_app, user):
    browser = TestApp(web_app)
    api = TestApp(api_app)

    ud = dict(uid="23", loginname="ck", password="klinger")
    resp = api.post_json("/user.add", ud, expect_errors=True)
    assert resp.status == "201 Created"
    assert resp.json == {"id": "23"}

    auth = web_app.utilities.get('authentication')
    assert isinstance(auth, uvcreha.auth.Auth) is True

    user = auth.from_credentials(ud)
    assert user.loginname == "ck"
    assert user.password.get_secret_value() == "klinger"

    ud['password'] = "wrong"
    user = auth.from_credentials(ud)
    assert user is None
    assert resp.request.environ.get('test.principal', None) is None

    ud = dict(loginname="ck", password="klinger")
    ud['form.trigger'] = "trigger.speichern"
    resp = browser.post("/login", ud)
    assert resp.status == "302 Found"
    assert resp.request.environ['test.principal'] is not None
