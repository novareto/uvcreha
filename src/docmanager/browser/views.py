import horseman.response
import horseman.meta
from typing import NamedTuple
from roughrider.workflow import State
from reiter.form import trigger
from reiter.view.meta import View
from docmanager.app import browser
from docmanager.browser.form import FormView
from docmanager.browser.layout import TEMPLATES
from docmanager.browser.openapi import generate_doc
from docmanager.models import User, UserPreferences, File, Document
from docmanager.request import Request
from docmanager.workflow import document_workflow


class UserDocument(NamedTuple):
    item: Document
    state: State


@browser.routes.register("/doc")
def doc_swagger(request: Request):
    return request.app.ui.response(
        TEMPLATES["swagger.pt"],
        request=request,
        url="/openapi.json"
    )


@browser.routes.register("/openapi.json")
def openapi(request: Request):
    open_api = generate_doc(request.app.routes)
    return horseman.response.reply(
        200,
        body=open_api.json(by_alias=True, exclude_none=True, indent=2),
        headers={"Content-Type": "application/json"}
    )


@browser.route("/flash")
def flash(request):
    flash_messages = request.utilities.get("flash")
    flash_messages.add(body="HELLO WORLD FROM REDIRECT.")
    return horseman.response.redirect("/")


@browser.route("/")
class LandingPage(View):

    def GET(self):
        user = self.request.user
        flash_messages = self.request.utilities.get("flash")
        flash_messages.add(body="HELLO WORLD.")
        return self.request.app.ui.response(
            TEMPLATES["index.pt"],
            request=self.request,
            user=user,
            view=self
        )

    def get_files(self, request, key):
        return request.database(File).find(username=key)

    def get_documents(self, request, username, az):
        docs = request.database(Document).find(username=username, az=az)
        for doc in docs:
            yield UserDocument(
                item=doc,
                state=document_workflow(doc).state)


@browser.route("/webpush")
def webpush(request: Request):
    return request.app.ui.response(
        TEMPLATES["webpush.pt"],
        layout_name="default",
        request=request
    )


@browser.route("/email_preferences")
class EditPreferences(FormView):

    title = "E-Mail Adresse ändern"
    description = "Edit your preferences."
    action = "preferences"
    model = UserPreferences

    @trigger("abbrechen", "Abbrechen", css="btn btn-secondary")
    def abbrechen(self, request):
        pass

    @trigger("update", "Update", css="btn btn-primary")
    def update(self, request):
        data = request.extract()["form"]
        form = self.setupForm(formdata=data)
        if not form.validate():
            return self.namespace(request, form=form, error=None)

        user = User(request.db_session)
        user.update(request.user.key, preferences=data.dict())
        return horseman.response.reply(200)

    def GET(self, request: Request):
        preferences = request.user.preferences.dict()
        form = self.setupForm(data=preferences)
        return self.namespace(request, form=form, error=None)
