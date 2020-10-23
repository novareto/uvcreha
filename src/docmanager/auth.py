import collections
from pathlib import Path
from chameleon import PageTemplateLoader
from horseman.prototyping import Environ


TEMPLATES = PageTemplateLoader(
    str((Path(__file__).parent / 'templates').resolve()), ".pt")


User = collections.namedtuple(
    'User', ['username', 'password', 'permissions'])


USERS = {
    'admin': User(
        username='admin',
        password='admin',
        permissions={'document.view'})
}


class Auth:

    def __init__(self, session, principal, **kwargs):
        self.session = session
        self.principal = principal

    def from_credentials(self, environ: Environ, credentials: dict) -> User:
        if (user := USERS.get(credentials['username'])):
            if credentials['password'] == user.password:
                return user
        return None

    def identify(self, environ: Environ) -> User:
        if (user := environ.get(self.principal, None)) is not None:
            return user
        session = environ[self.session]
        if (username := session.get('username', None)) is not None:
            user = USERS[username]
            environ[self.principal] = user
            return user
        return None

    def get_principal(self, environ):
        return environ[self.principal]

    def remember(self, environ: Environ, user: User):
        session = environ[self.session]
        session['username'] = user.username
        environ[self.principal] = user

    def __call__(self, app):
        def auth_application_wrapper(environ, start_response):
            self.identify(environ)
            return app(environ, start_response)
        return auth_application_wrapper
