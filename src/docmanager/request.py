import horseman.parsing
from horseman.meta import Overhead


class Request(Overhead):

    __slots__ = (
        'app', 'environ', 'route', 'data', 'method', '_extracted'
    )

    def __init__(self, app, environ, route):
        self.app = app
        self.environ = environ
        self.route = route
        self.method = environ['REQUEST_METHOD']
        self._data = {}
        self._extracted = False

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

    def get_flash_messages(self):
        from .models import Messages
        mes = []
        if messages := self.session.get('flashmessages'):
            mes = [message for message in Messages.parse_raw(messages).messages]
            self.session['flashmessages'] = []
        return mes

    def flash(self, message):
        from .models import Messages
        messages = self.session.get('flashmessages', None)
        if messages:
            messages = Messages.parse_raw(messages)
        else:
            messages = Messages()
        messages.messages.append(message)
        self.session['flashmessages'] = messages.json()
