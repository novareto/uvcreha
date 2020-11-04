from webtest import TestApp


def test_index(application):

    app = TestApp(application)
    resp = app.get('/')
    assert resp.status == '200 OK'


def test_add_user(application):

    app = TestApp(application)
    resp = app.post(
        '/user.add', {'nothing': 'at_all'},
        content_type='application/x-www-form-urlencoded',
        expect_errors=True
    )

    assert resp.json == {
         'errors': [
             {'loc': ['username'],
              'msg': 'field required',
              'type': 'value_error.missing'},
             {'loc': ['password'],
              'msg': 'field required',
              'type': 'value_error.missing'}],
        'name': 'docmanager.models.User',
        'type': 'Model validation',
    }
