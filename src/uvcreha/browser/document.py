import horseman.response
from horseman.http import Multidict
from reiter.form import trigger
from reiter.view.meta import View
from uvcreha.app import browser
from uvcreha.browser.form import Form, FormView
from uvcreha.browser.layout import TEMPLATES
from uvcreha.workflow import DocumentWorkflow, document_workflow
from ..models import Document, File


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
class DocumentEditForm(FormView):

    title = "Form"
    description = "Bitte füllen Sie alle Details"
    model = Document

    def update(self):
        super().update()
        self.context = self.request.database(
            self.model).find_one(**self.params)

    def get_initial_data(self):
        if self.context.item is not None:
            return self.context.item.dict()
        return {}

    def setupForm(self, data={}, formdata=Multidict()):
        _type = self.context.alternatives[self.context.content_type]
        form = Form.from_model(_type, only=("name", "surname", "iban"))
        form.process(data=data, formdata=formdata)
        return form

    @trigger("speichern", "Speichern", css="btn btn-primary")
    def speichern(self, request, data):
        binding = request.database(Document)
        document = binding.fetch(request.route.params.get("docid"))
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
        wf.transition_to(document_workflow.states.sent)
        binding.update(
            document.docid, item=doc_data, state=DocumentWorkflow.states.sent.name, **form_data
        )
        return horseman.response.Response.create(302, headers={"Location": "/"})
