import wtforms
import reiter.form
from horseman.http import Multidict
from docmanager.request import Request
from docmanager.browser.layout import template, TEMPLATES


class FormMeta(wtforms.meta.DefaultMeta):

    def render_field(inst, field, render_kw):
        class_ = "form-control"
        if field.errors:
            class_ += " is-invalid"
        render_kw.update({"class_": class_})
        return field.widget(field, **render_kw)


class Form(reiter.form.Form):

    def __init__(self, fields, prefix="", meta=FormMeta()):
        super().__init__(fields, prefix, meta)


class FormView(reiter.form.FormView):

    def setupForm(self, data={}, formdata=Multidict()):
        form = Form.from_model(self.model)
        form.process(data=data, formdata=formdata)
        return form

    @template(TEMPLATES["base_form.pt"], layout_name="default", raw=False)
    def GET(self, request: Request):
        form = self.setupForm()
        return {
            "form": form,
            "view": self,
            "error": None,
            "path": request.route.path
        }

    @template(TEMPLATES["base_form.pt"], layout_name="default", raw=False)
    def POST(self, request: Request):
        request.extract()
        return self.process_action(request)


class DocFormView(FormView):

    @template(TEMPLATES["base_form.pt"], layout_name="default", raw=False)
    def GET(self, request: Request, username: str, fileid: str, docid: str):
        form = self.setupForm()
        return {
            "form": form,
            "view": self,
            "error": None,
            "path": request.route.path
        }

    @template(TEMPLATES["base_form.pt"], layout_name="default", raw=False)
    def POST(self, request: Request, username: str, fileid: str, docid: str):
        request.extract()
        return self.process_action(request)
