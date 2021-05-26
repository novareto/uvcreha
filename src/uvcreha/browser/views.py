import horseman.response
import horseman.meta
from typing import NamedTuple
from roughrider.workflow import State
from reiter.form import trigger
from reiter.view.meta import View
from uvcreha.app import browser
from uvcreha.browser.form import FormView
from uvcreha.browser.layout import TEMPLATES
from uvcreha.request import Request
from uvcreha.workflow import document_workflow, file_workflow
from uvcreha import contenttypes


@browser.route("/")
class LandingPage(View):

    template = TEMPLATES["index.pt"]

    def GET(self):
        user = self.request.user
        flash_messages = self.request.utilities.get("flash")
        #flash_messages.add(body="HELLO WORLD.")
        return {"user": user}

    def get_files(self, key):
        ct = contenttypes.registry['file']
        files = ct.bind(self.request.database).find(uid=key)
        return files

    def get_documents(self, uid, az):
        ct = contenttypes.registry['document']
        docs = ct.bind(self.request.database).find(uid=uid, az=az)
        return docs


@browser.route("/webpush")
class Webpush(View):
    template = TEMPLATES["webpush.pt"]

    def GET(self):
        return dict(request=self.request)

    def POST(self):
        wp = self.request.app.utilities['webpush']
        wp.send(
            message="klaus",
            token=self.request.user.preferences.webpush_subscription
        )
        return dict(success='ok')
