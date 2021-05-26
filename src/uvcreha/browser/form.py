import wtforms
import reiter.form
from horseman.http import Multidict
from wtforms import widgets, SelectMultipleField
from wtforms_components import read_only
from uvcreha.browser.layout import TEMPLATES
from jsonschema_wtforms import Form as JSONForm


class MultiCheckboxField(SelectMultipleField):
    widget = widgets.ListWidget(prefix_label=False)
    option_widget = widgets.CheckboxInput()


class FormMeta(wtforms.meta.DefaultMeta):

    locales = ['de_DE', 'de']

    def render_field(inst, field, render_kw):
        if isinstance(field, MultiCheckboxField):
            class_ = "form-check"
        elif isinstance(field, wtforms.fields.core.BooleanField):
            class_ = "form-check"
        elif isinstance(field, wtforms.fields.core.SelectFieldBase._Option):
            class_ = "form-check-input"
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
            self._fields = {name: read_only(field)
                            for name, field in self._fields.items()}
        else:
            for key in names:
                self._fields[key] = read_only(self._fields[key])


class FormView(reiter.form.FormView):

    template = TEMPLATES["base_form.pt"]

    @property
    def action(self):
        return (
            self.request.environ['SCRIPT_NAME'] +
            self.request.route.path
        )

    def setupForm(self, data={}, formdata=Multidict()):
        raise NotImplementedError('Subclass needs to implement it.')

    def GET(self):
        form = self.setupForm()
        return dict(form=form, error=None)
