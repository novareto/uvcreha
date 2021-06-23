
import pytest
from frozendict import frozendict
from io import BytesIO


@pytest.fixture(scope="session")
def environ():
    return frozendict({
        'REQUEST_METHOD': 'GET',
        'SCRIPT_NAME': '',
        'PATH_INFO': '/',
        'QUERY_STRING': '',
        'SERVER_NAME': 'test_domain.com',
        'SERVER_PORT': '80',
        'HTTP_HOST': 'test_domain.com:80',
        'SERVER_PROTOCOL': 'HTTP/1.0',
        'wsgi.url_scheme': 'http',
        'wsgi.version': (1,0),
        'wsgi.run_once': 0,
        'wsgi.multithread': 0,
        'wsgi.multiprocess': 0,
        'wsgi.input': BytesIO(b""),
        'wsgi.errors': BytesIO()
    })


@pytest.fixture(scope="session")
def json_post_environ(environ):
    return frozendict({
        **environ,
        'REQUEST_METHOD': 'POST',
        'SCRIPT_NAME': '/app',
        'PATH_INFO': '/login',
        'QUERY_STRING': 'action=login&token=abcdef',
        'wsgi.input': BytesIO(
            b'''{"username": "test", "password": "test"}'''
        ),
    })


@pytest.fixture(scope="session")
def environ_with_user(environ):
    return frozendict({
        **environ,
        'test.principal': {
            'id': "SomeUser",
        },
    })
