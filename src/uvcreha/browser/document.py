import json
import jsonschema
import wtforms
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
from jsonschema_wtforms import Form as JSONForm
from ..models import Document, File, JSONSchemaRegistry


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
class DocumentEditForm(View):
    template = TEMPLATES["jsonform.pt"]
    title = "Form"
    description = "Bitte füllen Sie alle Details"

    def update(self):
        self.context = self.request.database(Document).find_one(
            **self.params)

    def GET(self):
        return {
            'schemaURL': self.request.route_path(
                'jsonschema', schema=self.context.content_type),
            'targetURL': self.request.route.path,
            'data': json.dumps(self.context.item or {})
        }

    def POST(self):
        data = self.request.extract()
        formdata = data.form.dict()
        schema = JSONSchemaRegistry[self.context.content_type]
        jsonschema.validate(instance=formdata, schema=schema)
        print(formdata)
        return {
            'schemaURL': self.request.route_path(
                'jsonschema', schema=self.context.content_type),
            'targetURL': self.request.route.path,
            'data': formdata
        }

@browser.route("/users/{uid}/files/{az}/docs/{docid}/edit_direct", name="doc.edit_direct")
class DocumentDirectEditForm(FormView):
    title = "Form"
    description = "Bitte füllen Sie alle Details"

    def update(self):
        self.context = self.request.database(Document).find_one(
            **self.params)

    def setupForm(self, data={}, formdata=Multidict()):
        schema = JSONSchemaRegistry[self.context.content_type]
        form = JSONForm.from_schema(schema)
        if data is None:
            if self.context.item:
                data = self.context.item.dict()

        form.process(data=data, formdata=formdata)
        return form

    @trigger("speichern", "Speichern", css="btn btn-primary")
    def speichern(self, request, data):
        formdata = data.form.dict()
        schema = JSONSchemaRegistry[self.context.content_type]
        jsonschema.validate(instance=formdata, schema=schema)
        print(formdata)
        return horseman.response.redirect(self.destination)
