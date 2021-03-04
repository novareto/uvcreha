import horseman.response
from horseman.http import Multidict
from reiter.form import trigger, FormView
from reiter.view.meta import View
from uvcreha.app import browser
from uvcreha.browser.form import Form
from uvcreha.browser.layout import TEMPLATES
from uvcreha.workflow import DocumentWorkflow, document_workflow
from ..models import Document


@browser.route("/users/{uid}/files/{az}/docs/{key}", name="index")
class DocumentIndex(View):
    template = TEMPLATES["index.pt"]

    def GET(self):
        doc = self.request.database(Document).fetch(self.params['uid'])
        if doc.state == "Inquiry":
            return horseman.response.redirect(
                self.request.app.routes.url_for(
                    "doc.edit", **self.params
                )
            )
        return dict(request=self.request, document=doc)


@browser.route("/users/{uid}/files/{az}/docs/{key}/edit", name="doc.edit"
)
class DocumentEditForm(FormView):

    title = "Form"
    description = "Bitte füllen Sie alle Details"
    action = "edit"
    model = Document

    def setupForm(self, data={}, formdata=Multidict()):
        form = Form.from_model(self.model, only=("name", "surname", "iban"))
        form.process(data=data, formdata=formdata)
        return form

    @trigger("speichern", "Speichern", css="btn btn-primary")
    def speichern(self, request, data):
        binding = request.database(Document)
        document = binding.fetch(request.route.params.get("key"))
        form = self.setupForm(formdata=data.form)
        if not form.validate():
            return {
                "form": form,
                "view": self,
                "error": None,
                "path": request.route.path,
            }
        doc_data = data.form.dict()
        form_data = request.route.params
        wf = document_workflow(document, request=request)
        wf.transition_to(DocumentWorkflow.states.sent)
        binding.update(
            item=doc_data, state=DocumentWorkflow.states.sent.name, **form_data
        )
        return horseman.response.Response.create(302, headers={"Location": "/"})
