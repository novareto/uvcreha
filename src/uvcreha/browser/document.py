import horseman.response
from horseman.http import Multidict
from reiter.form import trigger
from reiter.view.meta import View
from reiter.application.registries import NamedComponents
from uvcreha.app import browser
from uvcreha.browser.layout import TEMPLATES
from uvcreha.browser.form import Form, FormView
from uvcreha import contenttypes, jsonschema
from uvcreha.workflow import document_workflow


@browser.route("/users/{uid}/files/{az}/docs/{docid}", name="doc.view")
class DocumentIndex(View):
    template = TEMPLATES["document.pt"]

    def update(self):
        ct = contenttypes.registry['document']
        self.context = ct.bind(self.request.database).find_one(
            **self.params)

    def GET(self):
        if self.context.state is document_workflow.states.inquiry:
            return horseman.response.redirect(
                self.request.app.routes.url_for(
                    "doc.edit", **self.params
                )
            )
        return dict(request=self.request, document=self.context)


DocumentEdit = NamedComponents()


@browser.route(
    "/users/{uid}/files/{az}/docs/{docid}/edit",
    methods=['GET', 'POST'],
    name="doc.edit")
def document_edit_dispatch(request, **params):
    content_type = contenttypes.registry['document']
    context = content_type.bind(request.database).find_one(**params)
    form = DocumentEdit.get(context["content_type"], "default")
    form.content_type = content_type
    form.context = content_type.bind(request.database).find_one(**params)
    return form(request, **params)


@DocumentEdit.component('default')
class DefaultDocumentEditForm(FormView):
    title = "Form"
    description = "Bitte füllen Sie alle Details"
    content_type = None
    context = None

    def setupForm(self, data={}, formdata=Multidict()):
        schema = jsonschema.store.get(self.context['content_type'])
        form = Form.from_schema(schema)
        form.process(data=data, formdata=formdata)
        return form

    @trigger("speichern", "Speichern", css="btn btn-primary")
    def speichern(self, request, data):
        form = self.setupForm(formdata=data.form)
        if not form.validate():
            return {'form': form}
        self.content_type.bind(self.request.database).update(
            _key=self.context.id,
            state=document_workflow.states.sent.name,
            **data.form.dict()
        )
        return horseman.response.redirect(
            self.request.environ['SCRIPT_NAME'] + '/'
        )
