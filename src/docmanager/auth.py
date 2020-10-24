import collections
import wtforms.form
import wtforms.fields
import wtforms.validators
from pathlib import Path
from chameleon import PageTemplateLoader

import horseman.response
import roughrider.auth.meta
from horseman.prototyping import Environ
from horseman.meta import APIView, SentryNode
from horseman.parsing import parse
from .app import application
from .layout import template_endpoint

TEMPLATES = PageTemplateLoader(
    str((Path(__file__).parent / 'templates').resolve()), ".pt")


User = collections.namedtuple('User', ['username'])


class Auth:

    def __init__(self, session_key: str, login_path: str):
        self.session_key = session_key
        self.login_path = login_path

    @property
    def unauthorized(self):
        return horseman.response.Response.create(302, headers={
            'Location': self.login_path
        })

    @property
    def forbidden(self):
        return horseman.response.Response.create(403)

    def from_credentials(self, environ: Environ, credentials: dict) -> User:
        if (credentials['username'] == 'admin' and
            credentials['password'] == 'admin'):
            return User(username='admin')
        return None

    def identify(self, environ: Environ) -> User:
        if (user := environ.get('adhoc.principal', None)) is not None:
            return user
        session = environ[self.session_key]
        if (username := session.get('username', None)) is not None:
            user = User(username=username)
            environ['adhoc.principal'] = user
            return user
        return None

    def remember(self, environ: Environ, user: User):
        session = environ[self.session_key]
        session['username'] = user.username
        environ['adhoc.principal'] = user

    def __call__(self, app):
        def auth_application_wrapper(environ, start_response):
            user = self.identify(environ)
            if user is None:
                return self.unauthorized(environ, start_response)
            return app(environ, start_response)
        return auth_application_wrapper


class LoginForm(wtforms.form.Form):
    username = wtforms.fields.StringField(
        'Username', validators=(wtforms.validators.InputRequired(),))
    password = wtforms.fields.PasswordField(
        'Password', validators=(wtforms.validators.InputRequired(),))


@application.route('/login')
class LoginView(APIView):

    @template_endpoint(TEMPLATES['login.pt'])
    def GET(self, request, environ):
        form = LoginForm()
        return {'form': form, 'error': None}

    @template_endpoint(TEMPLATES['login.pt'])
    def POST(self, request, environ):
        data, files = parse(environ['wsgi.input'], request.content_type)
        form = LoginForm(data)
        if not form.validate():
            return {'form': form, 'error': 'form'}
        if (user := request.app.auth.from_credentials(
                environ, data.to_dict())) is not None:
            request.app.auth.remember(environ, user)
            print('Login Successfull')
            return horseman.response.Response.create(
                302, headers={'Location': '/'})
        return {'form': form, 'error': 'auth'}


def LogoutView(request, environ):
    request.session.store.clear(request.session.sid)
    return horseman.response.Response.create(
            302, headers={'Location': '/'})

