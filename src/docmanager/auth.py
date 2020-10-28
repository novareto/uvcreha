import collections
from pathlib import Path
from chameleon import PageTemplateLoader
from horseman.prototyping import Environ
from docmanager.request import Request
from docmanager.models import User


TEMPLATES = PageTemplateLoader(
    str((Path(__file__).parent / 'templates').resolve()), ".pt")


class Auth:

    def __init__(self, app):
        self.app = app

    def from_credentials(self, credentials: dict):
        USERS = self.app.db.connector.collection('users')
        if (user := USERS.get(credentials['username'])):
            if credentials['password'] == user.get('password'):
                user_class = self.app.models['user']
                return user_class(**user)
        return None

    def identify(self, environ: Environ):
        if (user := environ.get(self.app.config.env.user)) is not None:
            return user
        session = environ.get(self.app.config.env.session)
        if (user := session.get('user', None)) is not None:
            environ['self.app.config.env.user'] = user
            return user
        return None

    def remember(self, environ: Environ, user):
        session = environ.get(self.app.config.env.session)
        environ[self.app.config.env.user] = user
        session['user'] = user
        print('User in SESSION')

    def __call__(self, app):
        def auth_application_wrapper(environ, start_response):
            self.identify(environ)
            return app(environ, start_response)
        return auth_application_wrapper
