from horseman.types import Environ, WSGICallable
from horseman.response import Response
from uvcreha import contenttypes
from typing import Any, Callable, Set, Optional, Iterable
from roughrider import workflow


Filter = Callable[[Environ, WSGICallable, Any], Optional[Response]]


class Auth:

    filters: Iterable[Filter]

    def __init__(self, connector, user_key, session_key, filters=None):
        self.connector = connector
        self.user_key = user_key
        self.session_key = session_key
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
        if (user := environ.get(self.user_key)) is not None:
            return user

        session = environ[self.session_key]
        if (user_key := session.get(self.user_key, None)) is not None:
            db = self.connector.get_database()
            binding = contenttypes.registry['user'].bind(db)
            user = environ[self.user_key] = binding.fetch(user_key)
            return user

        return None

    def forget(self, environ: Environ):
        session = environ[self.session_key]
        session.store.clear(session.sid)

    def remember(self, environ: Environ, user):
        session = environ[self.session_key]
        session[self.user_key] = user['uid']
        environ[self.user_key] = user

    def __call__(self, app):

        def auth_application_wrapper(environ, start_response):
            user = self.identify(environ)
            for filter in self.filters:
                if (response := filter(environ, app, user)) is not None:
                    return response(environ, start_response)
            return app(environ, start_response)

        return auth_application_wrapper
