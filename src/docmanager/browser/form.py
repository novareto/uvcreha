import collections
import inspect
import typing
import pydantic
import wtforms
from dataclasses import dataclass
from horseman.meta import APIView
from docmanager.request import Request
from docmanager.browser.layout import template, TEMPLATES
from wtforms_pydantic.converter import Converter, model_fields


@dataclass
class Trigger:
    id: str
    title: str
    method: typing.Callable
    css: str

    def __call__(self, *args, **kwargs):
        return self.method(*args, **kwargs)


def trigger(id, title, css="btn btn-primary"):
    def mark_as_trigger(func):
        func.trigger = Trigger(
            id=f'trigger.{id}',
            title=title,
            css=css,
            method=func,
        )
        return func
    return mark_as_trigger


class FormMeta(wtforms.meta.DefaultMeta):

    def render_field(inst, field, render_kw):
        class_ = "form-control"
        if field.errors:
            class_ += " is-invalid"
        render_kw.update({"class_": class_})
        return field.widget(field, **render_kw)


class Form(wtforms.form.BaseForm):

    def __init__(self, fields, prefix="", meta=FormMeta()):
        super().__init__(fields, prefix, meta)

    @classmethod
    def from_model(cls, model, only=(), exclude=(), **overrides):
        return cls(Converter.convert(
            model_fields(model, only=only, exclude=exclude), **overrides
        ))


class FormViewMeta(type):

    def __init__(cls, name, bases, attrs):
        type.__init__(cls, name, bases, attrs)
        cls.triggers = getattr(cls, 'triggers', collections.OrderedDict())
        for name, member in attrs.items():
            if inspect.isfunction(member) and hasattr(member, 'trigger'):
                trigger = member.trigger
                cls.triggers[trigger.id] = trigger
                del member.trigger


class FormView(APIView, metaclass=FormViewMeta):

    title: str = ""
    description: str = ""
    action: str = ""
    method: str = "POST"
    model: pydantic.BaseModel

    @template(TEMPLATES["base_form.pt"], layout_name="default", raw=False)
    def GET(self, request: Request):
        form = self.setupForm()
        return {
            "form": form,
            "view": self,
            "error": None,
            "path": request.route.path
        }

    def POST(self, request: Request):
        for trigger_id in self.triggers.keys():
            data = request.extract()
            if trigger_id in data['form']:
                return self.triggers[trigger_id](self, request)
        raise KeyError("No action found")
