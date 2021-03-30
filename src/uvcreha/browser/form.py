import inspect
import wtforms
import reiter.form
import wtforms_pydantic
from pydantic import create_model
from horseman.http import Multidict
from uvcreha.browser.layout import TEMPLATES
from flatten_dict import flatten, unflatten
from wtforms import widgets, SelectMultipleField


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


class Form(wtforms_pydantic.Form):

    def __init__(self, fields, prefix="", meta=FormMeta()):
        super().__init__(fields, prefix, meta)


class FormView(reiter.form.FormView):

    template = TEMPLATES["base_form.pt"]

    @property
    def action(self):
        return (
            self.request.environ['SCRIPT_NAME'] +
            self.request.route.path
        )

    def setupForm(self, data={}, formdata=Multidict()):
        form = Form.from_model(self.model)
        form.process(data=data, formdata=formdata)
        return form

    def GET(self):
        form = self.setupForm()
        return dict(form=form, error=None)


class Composer:

    factory = Form

    def __init__(self, model):
        self.model = model

    @classmethod
    def composed_model(cls, name, **objs):
        fields = {}
        for name, _type in objs.items():
            if not inspect.isclass(_type):
                fields[name] = (_type.__class__, _type)
            else:
                fields[name] = (_type, ...)
        model = create_model(name, **fields)
        return cls(model)

    def field(self, name, model=None):
        if model is None:
            model = self.model
        stack = name.split('.', 1)
        if len(stack) == 2:
            model = model.__fields__[stack[0]].type_
            return self.field(stack[1], model)
        else:
            return model.__fields__[stack[0]]

    def fields(self, *names):
        for name in names:
            yield (name, self.field(name))

    def form_fields(self, *names):
        return wtforms_pydantic.Converter.convert(
            dict(self.fields(*names))
        )

    def default_values(self):
        if not inspect.isclass(self.model):
            return flatten(self.model.dict(), reducer='dot')
        return {}

    def form(self, *names):
        return self.factory(self.form_fields(*names))

    def format(self, data):
        return unflatten(data, splitter='dot')
