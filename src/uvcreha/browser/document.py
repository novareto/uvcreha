import horseman.response
from horseman.http import Multidict
from reiter.form import trigger
from reiter.view.meta import View
from uvcreha.app import browser
from uvcreha.browser.layout import TEMPLATES
from uvcreha.browser.form import Form, FormView
from uvcreha import contenttypes, jsonschema
from uvcreha.workflow import document_workflow


@browser.register("/users/{uid}/files/{az}/docs/{docid}", name="doc.view")
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


@browser.register(
    "/users/{uid}/files/{az}/docs/{docid}/edit", name="doc.edit")
class DocumentEditForm(FormView):
    title = "Form"
    description = "Bitte füllen Sie alle Details"

    def update(self):
        ct = contenttypes.registry['document']
        self.context = ct.bind(self.request.database).find_one(
            **self.params)

    def setupForm(self, data={}, formdata=Multidict()):
        schema = jsonschema.store.get(
            self.context.data['content_type'])
        form = Form.from_schema(schema)
        form.process(data=data, formdata=formdata)
        return form

    @trigger("speichern", "Speichern", css="btn btn-primary")
    def speichern(self, request, data):
        form = self.setupForm(formdata=data.form)
        if not form.validate():
            return {'form': form}
        raise NotImplementedError(form)
        return horseman.response.redirect(
            self.request.environ['SCRIPT_NAME'] + '/'
        )
