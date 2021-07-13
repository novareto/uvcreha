import json
import horseman.response
from multidict import MultiDict
from reiter.form import trigger
from reiter.application.registries import NamedComponents
from uvcreha.app import browser
from uvcreha.browser.views import View
from uvcreha.browser.layout import TEMPLATES
from uvcreha.browser.form import Form, FormView
from uvcreha import contenttypes, jsonschema
from uvcreha.workflow import document_workflow
from jsonschema_wtforms import schema_fields


@browser.register("/users/{uid}/files/{az}/docs/{docid}", name="doc.view")
class DocumentIndex(View):
    template = TEMPLATES["document.pt"]

    def update(self):
        ct = contenttypes.registry["document"]
        self.context = ct.bind(self.request.database).find_one(**self.params)

    def GET(self):
        if self.context.state is document_workflow.states.inquiry:
            return horseman.response.redirect(
                self.request.app.routes.url_for("doc.edit", **self.params)
            )
        return dict(
            request=self.request,
            document=self.context,
            json=json.dumps(dict(self.context), indent=4)
        )


DocumentEdit = NamedComponents()


@browser.register(
    "/users/{uid}/files/{az}/docs/{docid}/edit",
    methods=['GET', 'POST'],
    name="doc.edit")
def document_edit_dispatch(request, **params):
    content_type = contenttypes.registry['document']
    context = content_type.bind(request.database).find_one(**params)
    form = DocumentEdit.get(context["content_type"], DefaultDocumentEditForm)
    form.content_type = content_type
    form.context = content_type.bind(request.database).find_one(**params)
    return form(request, **params)()


@DocumentEdit.component('default')
class DefaultDocumentEditForm(FormView):
    title = "Form"
    description = "Bitte füllen Sie alle Details"
    content_type = None
    context = None

    def get_fields(self):
        name, version = self.context["content_type"].rsplit(".", 1)
        schema = jsonschema.documents_store.get(name, version)
        return schema_fields(schema.value)

    def setupForm(self, formdata=MultiDict()):
        fields = self.get_fields()
        form = Form(fields)
        form.process(data=self.context, formdata=formdata)
        return form

    @trigger("Speichern", css="btn btn-primary", order=10)
    def save(self, request, data):
        #data = request.extract()["form"]
        data = request.get_data().form
        form = self.setupForm(formdata=data)
        if not form.validate():
            return {"form": form}

        if self.context.state != document_workflow.states.sent:
            wf = document_workflow(self.context, request=request)
            wf.transition_to(document_workflow.states.sent)
        doc = contenttypes.registry["document"].bind(self.request.database)
        response = doc.update(
            request.route.params['docid'],
            item=data.dict(),
            state=self.context.state.name
        )
        return self.redirect("/")

    @trigger("Abbrechen", css="btn btn-secondary", order=20)
    def cancel(self, request, data):
        return self.redirect("/")
