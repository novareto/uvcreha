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
        return dict(request=self.request, document=self.context)


DocumentEdit = NamedComponents()


@browser.register(
    "/users/{uid}/files/{az}/docs/{docid}/edit",
    methods=['GET', 'POST'],
    name="doc.edit")
def document_edit_dispatch(request, **params):
    content_type = contenttypes.registry['document']
    context = content_type.bind(request.database).find_one(**params)
    print(context["content_type"])
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

    def setupForm(self, data={}, formdata=Multidict()):
        schema = jsonschema.store.get(self.context['content_type'])
        form = Form.from_schema(schema)
        form.process(data=data, formdata=formdata)
        return form

    @trigger("save", "Save", css="btn btn-primary")
    def save(self, request):
        data = request.extract()["form"]
        form = self.setupForm(formdata=data)
        if not form.validate():
            return {"form": form}
        doc = contenttypes.registry["document"].bind(self.request.database)
        wf = document_workflow(doc)
        wf.transition_to(document_workflow.states.sent)
        doc.update(
            request.params['docid'],
            item=data.dict(),
            state=doc['state']
        )
        return self.redirect("/")

    @trigger("cancel", "Cancel", css="btn btn-primary")
    def cancel(self, request):
        return self.redirect("/")
