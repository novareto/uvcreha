import cgi
import collections
import horseman.parsing
from horseman.meta import Overhead
from reiter.application.request import Request as BaseRequest


class Request(BaseRequest):

    _db = None

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
