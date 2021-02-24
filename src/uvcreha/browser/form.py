import wtforms
import reiter.form
from horseman.http import Multidict
from uvcreha.browser.layout import TEMPLATES
from uvcreha.models import Document


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

    def GET(self):
        form = self.setupForm()
        return dict(form=form, error=None)
