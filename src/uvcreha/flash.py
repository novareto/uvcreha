import reiter.application.events
from typing import NamedTuple
from uvcreha.app import events


class Message(NamedTuple):
    body: str
    type: str


class SessionMessages:
    def __init__(self, session, key="flashmessages"):
        self.key = key
        self.session = session

    def __iter__(self):
        if self.key in self.session:
            while self.session[self.key]:
                yield Message(**self.session[self.key].pop(0))
                self.session.save()

    def add(self, body: str, type: str = "info"):
        if self.key in self.session:
            messages = self.session[self.key]
        else:
            messages = self.session[self.key] = []
        messages.append({"type": type, "body": body})
        self.session.save()


@events.subscribe(reiter.application.events.RequestCreated)
def flash_utility(event):
    flash = event.app.utilities["flash"](event.request.environ)
    event.request.utilities.register(flash, "flash")
