from collections import deque
from docmanager.models import Message


class SessionMessages:

    def __init__(self, request, key='flashmessages'):
        self.key = key
        self.request = request

    def __iter__(self):
        if self.key in self.session:
            messages = deque(self.session[self.key])
            while self.session[self.key]:
                yield Message(self.session[self.key].pop(0))

    def add(self, message: Message):
        messages = self.session.get('flashmessages', [])
        messages.append(message.dict())


class Flash:

    def __init__(self, source=SessionMessages):
        self.source = source

    def messages(self, request):
        return self.source(request)
