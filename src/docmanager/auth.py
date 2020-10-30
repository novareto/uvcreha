from horseman.prototyping import Environ
import docmanager.sql


class Auth:

    def __init__(self, database, config):
        self.database = database
        self.config = config

    def from_credentials(self, credentials: dict) -> docmanager.sql.User:
        session = database.new_session()
        user = session.query(docmanager.sql.SQLUser).filter_by(
            **credentials)
        if user is not None:
            return user.from_orm(user).dict()
        return None

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
