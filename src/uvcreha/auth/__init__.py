from horseman.types import Environ, WSGICallable
from horseman.response import Response
from uvcreha import contenttypes
from typing import Any, Callable, Set, Optional, Iterable
from roughrider import workflow


Filter = Callable[[Environ, WSGICallable, Any], Optional[Response]]


class Auth:

    filters: Iterable[Filter]

    def __init__(self, connector, config, filters=None):
        self.connector = connector
        self.config = config
        if filters is None:
            filters = []
        self.filters = filters

    def from_credentials(self, credentials: dict):
        db = self.connector.get_database()
        binding = contenttypes.registry['user'].bind(db)
        # We use either loginname or email
        user = binding.find_one(
            loginname=credentials['loginname'],
            password=credentials['password']
        )
        if user is not None:
            return user
        return binding.find_one(
            email=credentials['loginname'],
            password=credentials['password']
        )

    def identify(self, environ: Environ):
        if (user := environ.get(self.config.user)) is not None:
            return user

        session = environ[self.config.session]
        if (user_key := session.get(self.config.user, None)) is not None:
            db = self.connector.get_database()
            binding = contenttypes.registry['user'].bind(db)
            user = environ[self.config.user] = binding.fetch(user_key)
            return user

        return None

    def remember(self, environ: Environ, user):
        session = environ[self.config.session]
        session[self.config.user] = user['uid']
        environ[self.config.user] = user

    def __call__(self, app):

        def auth_application_wrapper(environ, start_response):
            user = self.identify(environ)
            for filter in self.filters:
                if (response := filter(environ, app, user)) is not None:
                    return response(environ, start_response)
            return app(environ, start_response)

        return auth_application_wrapper
