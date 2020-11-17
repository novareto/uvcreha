from collections import deque
from docmanager.models import Message


class SessionMessages:

    def __init__(self, request, key="flashmessages"):
        self.key = key
        self.request = request

    def __iter__(self):
        if self.key in self.request.session:
            messages = deque(self.request.session[self.key])
            while self.request.session[self.key]:
                yield Message(**self.request.session[self.key].pop(0))

    def add(self, body: str, type: str = "info"):
        if self.key in self.request.session:
            messages = self.request.session["flashmessages"]
        else:
            messages = self.request.session["flashmessages"] = []

        message = Message(type=type, body=body)
        messages.append(message.dict())


class Flash:

    def __init__(self, source=SessionMessages):
        self.source = source

    def __call__(self, request):
        return self.source(request)
