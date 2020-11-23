from horseman.prototyping import Environ
from horseman.response import Response
from docmanager.db import User


class Auth:

    unprotected = {'/login', '/webpush'}

    def __init__(self, model, config):
        self.model = model
        self.config = config

    def from_credentials(self, credentials: dict):
        return self.model.find_one(
            username=credentials['username'],
            password=credentials['password']
        )

    def identify(self, environ: Environ):
        if (user := environ.get(self.config.user)) is not None:
            return user
        session = environ.get(self.config.session)
        if (user := session.get(self.config.user, None)) is not None:
            environ[self.config.user] = user
            return user
        return None

    def remember(self, environ: Environ, user):
        session = environ.get(self.config.session)
        session[self.config.user] = environ[self.config.user] = user

    def __call__(self, app):
        def auth_application_wrapper(environ, start_response):
            user = self.identify(environ)
            if user is not None or environ['PATH_INFO'] in self.unprotected:
                return app(environ, start_response)
            return Response.create(
                302, headers={'Location': '/login'}
            )(environ, start_response)
        return auth_application_wrapper


def plugin(app, config, user_model=User, name="authentication"):
    user = user_model(app.database.session)
    auth = Auth(user, config.env)
    app.plugins.register(auth, name=name)
    app.middlewares.register(auth, order=0)  # very first.
    return app
