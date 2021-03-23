import horseman.response
from horseman.http import Multidict
from reiter.form import trigger
from reiter.view.meta import View
from uvcreha.app import browser
from uvcreha.browser.composed import ComposedView
from uvcreha.browser.form import Form, FormView
from uvcreha.browser.layout import TEMPLATES
from uvcreha.browser.crud import ModelForm
from uvcreha.workflow import document_workflow
from wtforms_pydantic import model_fields
from ..models import Document, File


@browser.route("/test")
class ComposedDocument(ComposedView):
    template = TEMPLATES["composed.pt"]

    def GET(self):
        return {'innerpage': self.page.GET()}


@ComposedDocument.pages.component('default')
class DefaultView(View):
    title = 'Default'

    def GET(self):
        return 'My default View'


@ComposedDocument.pages.component('other')
class OtherView(View):
    title = 'Other view'

    def GET(self):
        return 'My other View'


@browser.route("/users/{uid}/files/{az}/docs/{docid}", name="doc.view")
class DocumentIndex(View):
    template = TEMPLATES["document.pt"]

    def GET(self):
        doc = self.request.database(Document).fetch(self.params['docid'])
        wf = document_workflow(doc)
        if wf.state is document_workflow.states.inquiry:
            return horseman.response.redirect(
                self.request.app.routes.url_for(
                    "doc.edit", **self.params
                )
            )
        return dict(request=self.request, document=doc)


@browser.route("/users/{uid}/files/{az}/docs/{docid}/edit", name="doc.edit"
)
class DocumentEditForm(ModelForm):

    title = "Form"
    description = "Bitte füllen Sie alle Details"
    model = Document

    def update(self):
        super().update()
        self.context = self.request.database(
            self.model).find_one(**self.params)
        self._type = self.context.alternatives[self.context.content_type]
        self.subitem = self.context.item or self._type.construct()

    def get_initial_data(self):
        if self.subitem is not None:
            return self.subitem.dict()
        return {}

    def fields(self, exclude=(), only=()):
        return model_fields(self._type, exclude=exclude, only=only)

    @trigger("speichern", "Speichern", css="btn btn-primary")
    def speichern(self, request, data):
        form = self.setupForm(formdata=data.form)
        if not form.validate():
            return {"form": form}
        item_data = self.subitem.dict()
        item_data.update(data.form.dict())
        wf = document_workflow(document, request=request)
        wf.transition_to(document_workflow.states.sent)
        self.request.database(self.model).update(
            self.context.__key__,
            item=item_data,
            state=document_workflow.states.sent.name,
        )
        return horseman.response.redirect("/")
