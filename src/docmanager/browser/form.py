import wtforms
import reiter.form
from horseman.response import reply
from horseman.http import Multidict
from docmanager.request import Request
from docmanager.browser.layout import UI, TEMPLATES
from docmanager.models import Document


class FormMeta(wtforms.meta.DefaultMeta):

    def render_field(inst, field, render_kw):
        if isinstance(field, wtforms.fields.core.BooleanField):
            class_ = "form-check"
        else:
            class_ = "form-control"
        if field.errors:
            class_ += " is-invalid"
        render_kw.update({"class_": class_})
        return field.widget(field, **render_kw)


class Form(reiter.form.Form):

    def __init__(self, fields, prefix="", meta=FormMeta()):
        super().__init__(fields, prefix, meta)


class FormView(reiter.form.FormView):

    template = TEMPLATES["base_form.pt"]

    def setupForm(self, data={}, formdata=Multidict()):
        form = Form.from_model(self.model)
        form.process(data=data, formdata=formdata)
        return form

    def GET(self, request: Request):
        form = self.setupForm()
        return UI.response(
            self.template,
            request=request,
            form=form,
            view=self,
            error=None
        )

    def POST(self, request: Request):
        request.extract()
        return self.process_action(request)


class DocFormView(FormView):

    def GET(self, request: Request, **data):
        doc = request.database(Document).fetch(request.route.params['key'])
        if doc.item:
            data.update(doc.item.dict())
        form = self.setupForm(data=data)
        return UI.response(
            self.template,
            form=form,
            view=self,
            error=None
        )

    def POST(self, request: Request, **data):
        request.extract()
        return self.process_action(request)
