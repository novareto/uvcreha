from webtest import TestApp


def test_index(application):

    app = TestApp(application)
    resp = app.get('/')
    assert resp.status == '200 OK'
