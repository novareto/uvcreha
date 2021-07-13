import wtforms
import reiter.form
from abc import ABC, abstractmethod
from horseman.http import HTTPError
from wtforms import widgets, SelectMultipleField
from wtforms_components import read_only
from wtforms.fields.simple import MultipleFileField
from jsonschema_wtforms import Form as JSONForm
from uvcreha import jsonschema
from uvcreha.browser.layout import TEMPLATES
from uvcreha.browser.resources import f_input_group
from uvcreha.browser.views import layout_rendering


class MultiCheckboxField(SelectMultipleField):
    widget = widgets.ListWidget(prefix_label=False)
    option_widget = widgets.CheckboxInput()


class FormMeta(wtforms.meta.DefaultMeta):

    locales = ["de_DE", "de"]

    def render_field(inst, field, render_kw):
        if isinstance(field, MultipleFileField):
            f_input_group.need()
        if isinstance(field, MultiCheckboxField):
            class_ = "form-check"
        elif isinstance(field, wtforms.fields.core.BooleanField):
            class_ = "form-check"
        elif isinstance(field, wtforms.fields.core.SelectFieldBase._Option):
            class_ = "form-check-input"
        elif isinstance(field, wtforms.fields.core.RadioField):
            class_ = "form-check"
        else:
            class_ = "form-control"
        if field.errors:
            class_ += " is-invalid"
        render_kw.update({"class_": class_})
        return field.widget(field, **render_kw)


class Form(JSONForm):
    def __init__(self, fields, prefix="", meta=FormMeta()):
        super().__init__(fields, prefix, meta)

    def readonly(self, names):
        if names is ...:
            self._fields = {
                name: read_only(field) for name, field in self._fields.items()
            }
        else:
            for key in names:
                self._fields[key] = read_only(self._fields[key])


class FormView(reiter.form.FormView):

    template = TEMPLATES["base_form.pt"]
    render = layout_rendering

    @property
    def action(self):
        return (
            self.request.environ["SCRIPT_NAME"] + self.request.route.path
        )

    @abstractmethod
    def get_fields(self):
        pass

    def setupForm(self, data=None, formdata=None):
        fields = self.get_fields()
        form = Form(fields)
        form.process(data=data, formdata=formdata)
        return form

    def GET(self):
        form = self.setupForm()
        return dict(form=form, error=None)

    def POST(self):
        data = self.request.extract()
        action = data.form.get('form.trigger')  # can be None.
        if action:
            return self.process_action(action)
        return HTTPError(400)
