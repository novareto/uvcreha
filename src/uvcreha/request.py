from horseman.http import Query
from reiter.application.request import Request as BaseRequest


class Request(BaseRequest):

    __slots__ = (
        '_db',
        'query',
    )

    def __init__(self, app, environ, route):
        super().__init__(app, environ, route)
        self._db = None
        self.query = Query.from_environ(environ)

    @property
    def session(self):
        return self.environ.get(self.app.config.env.session)

    @property
    def user(self):
        return self.environ.get(self.app.config.env.user)

    @property
    def database(self):
        if self._db is None:
            self._db = self.app.connector.get_database()
        return self._db
