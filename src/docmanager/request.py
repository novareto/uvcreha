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



    #@property
    #def flash(self):
    #    if messages := self.session.get('flashmessages'):
    #        return [message for message in Messages.parse_raw(messages).messages]
    #    return []

    #@flash.setter
    #def flash(self, message: Message):
    #    messages = self.session.get('flashmessages', Messages())
    #    messages.messages.append(message)
    #    self.session['flashmessages'] = messages.json()
