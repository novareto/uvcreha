from horseman.prototyping import Environ


class Auth:

    def __init__(self, model, config):
        self.model = model
        self.config = config

    def from_credentials(self, credentials: dict):
        return self.model.find_one(
            key=credentials['username'], password=credentials['password'])

    def identify(self, environ: Environ):
        if (user := environ.get(self.config.user)) is not None:
            return user
        session = environ.get(self.config.session)
        if (user := session.get('user', None)) is not None:
            environ[self.config.user] = user
            return user
        return None

    def remember(self, environ: Environ, user):
        session = environ.get(self.config.session)
        environ[self.config.user] = user
        session['user'] = user

    def __call__(self, app):
        def auth_application_wrapper(environ, start_response):
            self.identify(environ)
            return app(environ, start_response)
        return auth_application_wrapper
