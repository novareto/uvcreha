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


def test_add_user_ok(application):
    app = TestApp(application)
    resp = app.post(
        '/user.add', dict(username='cklinger', password='klinger'),
        #content_type='application/x-www-form-urlencoded',
        expect_errors=True
    )
    assert resp.status == "201 Created"
    assert resp.json == {'id': 'cklinger'} 


def test_get_user(application):
    app = TestApp(application)
    resp = app.get('/users/cklinger')
    assert resp.status == "200 OK"
    assert resp.json['key'] == 'cklinger' 


def test_add_folder(application):
    app = TestApp(application)
    resp = app.put('/users/cklinger/folder.add', dict(az='4711'))
    assert resp.status == "201 Created"
    assert resp.json['az'] == '4711'

def test_get_folder(application):
    app = TestApp(application)
    resp = app.get('/users/cklinger/folders/4711')
    assert resp.status == "200 Ok"
    assert resp.json['az'] == '4711'


def test_add_file(application):
    app = TestApp(application)
    resp = app.put('/users/cklinger/folders/4711/doc.add', 
        dict(body='Some Doc', state='Submitted', content_type='default'))
    assert resp.status == "201 Created"
    assert resp.json['az'] == '4711'

