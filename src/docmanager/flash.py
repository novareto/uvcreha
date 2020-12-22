from docmanager.app import browser
from docmanager.models import Message


class SessionMessages:

    def __init__(self, session, key="flashmessages"):
        self.key = key
        self.session = session

    def __iter__(self):
        if self.key in self.session:
            while self.session[self.key]:
                print("MESSAGES READED", self.session[self.key])
                yield Message(**self.session[self.key].pop(0))
                self.session[self.key] = self.session[self.key][:]

    def add(self, body: str, type: str = "info"):
        if self.key in self.session:
            messages = self.session[self.key]
        else:
            messages = self.session[self.key] = []

        message = Message(type=type, body=body)
        messages.append(message.dict())


@browser.subscribe('request_created')
def flash_utility(app, request):
    flash = SessionMessages(request.session)
    request.utilities.register(flash, 'flash')
