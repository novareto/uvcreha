from horseman.http import Query
from reiter.application.request import Request as BaseRequest


class Request(BaseRequest):

    __slots__ = ("query", "_db")

    def __init__(self, app, environ, route):
        super().__init__(app, environ, route)
        self._db = None
        self.query = Query.from_environ(environ)

    @property
    def user(self):
        return self.app.utilities["authentication"].identify(self.environ)

    @property
    def database(self):
        """Lazy database access."""
        if self._db is None:
            self._db = self.app.utilities["arango"].get_database()
        return self._db
