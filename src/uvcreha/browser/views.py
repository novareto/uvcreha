from reiter.view.meta import View
from uvcreha.app import browser
from uvcreha.browser.layout import TEMPLATES
from uvcreha import contenttypes


@browser.register("/")
class LandingPage(View):

    template = TEMPLATES["index.pt"]

    def GET(self):
        user = self.request.user
        # flash_messages = self.request.utilities.get("flash")
        # flash_messages.add(body="HELLO WORLD.")
        self.request.app.utilities['amqp'].send(
            {'test': 'YEAH'}, key='object.add'
        )
        return {"user": user}

    def get_files(self, key):
        ct = contenttypes.registry["file"]
        files = ct.bind(self.request.database).find(uid=key)
        return files

    def get_documents(self, uid, az):
        ct = contenttypes.registry["document"]
        docs = ct.bind(self.request.database).find(uid=uid, az=az)
        return docs


@browser.register("/webpush")
class Webpush(View):
    template = TEMPLATES["webpush.pt"]

    def GET(self):
        return dict(request=self.request)

    def POST(self):
        wp = self.request.app.utilities["webpush"]
        wp.send(
            message="klaus",
            token=self.request.user.preferences.webpush_subscription
        )
        return dict(success="ok")
