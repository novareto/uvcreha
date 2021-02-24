import horseman.response
import horseman.meta
from typing import NamedTuple
from roughrider.workflow import State
from reiter.form import trigger
from reiter.view.meta import View
from uvcreha.app import browser
from uvcreha.browser.form import FormView
from uvcreha.browser.layout import TEMPLATES
from uvcreha.browser.openapi import generate_doc
from uvcreha.models import User, UserPreferences, File, Document
from uvcreha.request import Request
from uvcreha.workflow import document_workflow, file_workflow


class UserDocument(NamedTuple):
    item: Document
    state: State


class UserFile(NamedTuple):
    item: File
    state: State
    url: str


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

    template = TEMPLATES["index.pt"]

    def GET(self):
        user = self.request.user
        flash_messages = self.request.utilities.get("flash")
        flash_messages.add(body="HELLO WORLD.")
        return {"user": user}

    def get_files(self, key):
        files = self.request.database(File).find(uid=key)
        for file in files:
            state = file_workflow(file).state
            if state is file_workflow.states.created:
                url = self.request.app.routes.url_for(
                    'file_register', az=file.az, uid=file.uid)
            else:
                url = self.request.app.routes.url_for(
                    'file_index', az=file.az, uid=file.uid)
            yield UserFile(
                item=file,
                url=url,
                state=state)

    def get_documents(self, uid, az):
        docs = self.request.database(Document).find(uid=uid, az=az)
        for doc in docs:
            yield UserDocument(
                item=doc,
                state=document_workflow(doc).state)


@browser.route("/users/{uid}/files/{az}", name="file_index")
class FileIndex(View):
    template = TEMPLATES["file_view.pt"]

    def GET(self):
        context = self.request.database(File).find_one(**self.params)
        return dict(request=self.request, context=context)



@browser.route("/webpush")
def webpush(request: Request):
    return request.app.ui.response(
        TEMPLATES["webpush.pt"],
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
            return {"form": form}

        user = User(request.db_session)
        user.update(request.user.key, preferences=data.dict())
        return self.redirect("/")

    def GET(self, request: Request):
        preferences = request.user.preferences.dict()
        form = self.setupForm(data=preferences)
        return {"form": form}
