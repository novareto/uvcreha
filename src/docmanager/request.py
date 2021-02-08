import cgi
import collections
import horseman.parsing
from horseman.meta import Overhead
from horseman.http import Query
from roughrider.routing.components import RoutingRequest
from reiter.application.registries import NamedComponents


ContentType = collections.namedtuple(
        'ContentType', ['raw', 'mimetype', 'options'])


class Request(RoutingRequest):

    __slots__ = (
        '_data'
        '_db',
        '_extracted',
        'app',
        'content_type',
        'environ',
        'method',
        'route',
        'query',
        'utilities',
    )

    def __init__(self, app, environ, route):
        self._data = {}
        self._db = None
        self._extracted = False
        self.app = app
        self.environ = environ
        self.method = environ['REQUEST_METHOD'].upper()
        self.route = route
        self.utilities = NamedComponents()
        if 'CONTENT_TYPE' in self.environ:
            ct = self.environ['CONTENT_TYPE']
            self.content_type = ContentType(ct, *cgi.parse_header(ct))
        else:
            self.content_type = None
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
        
    def set_data(self, data):
        self._data = data
            
    def get_data(self):
        return self._data
        
    def extract(self):
        if not self._extracted:
            self._extracted = True
            if content_type := self.content_type:
                self.set_data(horseman.parsing.parse(
                    self.environ['wsgi.input'], content_type.raw))
        return self.get_data()
