import horseman.parsing
from horseman.meta import Overhead
from docmanager.registries import NamedComponents


class Request(Overhead):

    __slots__ = (
        '_data'
        '_extracted',
        'app',
        'environ',
        'method',
        'route',
        'utilities',
    )

    def __init__(self, app, environ, route):
        self._data = {}
        self._extracted = False
        self.app = app
        self.environ = environ
        self.method = environ['REQUEST_METHOD']
        self.route = route
        self.utilities = NamedComponents()

    @property
    def content_type(self):
        if self.method in ('POST', 'PATCH', 'PUT'):
            return self.environ.get('CONTENT_TYPE')

    @property
    def session(self):
        return self.environ.get(self.app.config.env.session)

    @property
    def db_session(self):
        # Returns the session
        return self.app.database.session

    @property
    def user(self):
        return self.environ.get(self.app.config.env.user)

    def set_data(self, data):
        self._data = data

    def get_data(self):
        return self._data

    def extract(self):
        if self._extracted:
            return self.get_data()

        self._extracted = True
        if content_type := self.content_type:
            form, files = horseman.parsing.parse(
                self.environ['wsgi.input'], content_type)
            self.set_data({'form': form, 'files': files})

        return self.get_data()
