from horseman.meta import Overhead
from roughrider.validation.types import Validatable


class Request(Overhead, Validatable):

    __slots__ = (
        'app', 'environ', 'params', 'data', 'method', 'content_type'
    )

    def __init__(self, app, environ, session, **params):
        self.app = app
        self.environ = environ
        self.params = params
        self.data = {}
        self.method = environ['REQUEST_METHOD']
        if self.method in ('POST', 'PATCH', 'PUT'):
            self.content_type = environ.get('CONTENT_TYPE')
        else:
            self.content_type = None

    def set_data(self, data):
        self.data = data

    @property
    def session(self):
        return self.environ.get(self.app.config.env.principal_key)

    @property
    def principal(self):
        return self.environ.get(self.app.config.env.principal_key)
