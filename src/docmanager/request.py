from horseman.meta import Overhead
from roughrider.validation.types import Validatable
from .utils.flashmessages import Message, Messages


class Request(Overhead, Validatable):

    __slots__ = (
        'app', 'environ', 'route', 'data', 'method',
    )

    def __init__(self, app, environ, route):
        self.app = app
        self.environ = environ
        self.route = route
        self.method = environ['REQUEST_METHOD']
        self.data = {}

    @property
    def content_type(self):
        if self.method in ('POST', 'PATCH', 'PUT'):
            return self.environ.get('CONTENT_TYPE')

    def set_data(self, data):
        self.data = data

    @property
    def session(self):
        return self.environ.get(self.app.config.env.session)

    @property
    def user(self):
        return self.environ.get(self.app.config.env.user)

    @property
    def flash(self):
        if messages := self.session.get('flashmessages'):
            return [message for message in Messages.parse_raw(messages).messages]
        return []
   
    @flash.setter
    def flash(self, message: Message):
        messages = self.session.get('flashmessages', Messages())
        messages.messages.append(message)
        self.session['flashmessages'] = messages.json()
