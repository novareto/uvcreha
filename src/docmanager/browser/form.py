import wtforms
import collections
import pydantic
from horseman.meta import APIView
from docmanager.request import Request
from docmanager.browser.layout import template, TEMPLATES


class Triggers(collections.OrderedDict):
    def register(self, name, title=None, _class="btn btn-primary"):
        def add_trigger(method):
            tid = f"trigger.{name}"
            self[tid] = {
                "id": tid,
                "title": title or name,
                "method": method,
                "class": _class,
            }
            return method

        return add_trigger


class CustomBaseForm(wtforms.Form):
    class Meta(wtforms.meta.DefaultMeta):
        def render_field(inst, field, render_kw):
            class_ = "form-control"
            if field.errors:
                class_ += " is-invalid"
            render_kw.update({"class_": class_})
            return field.widget(field, **render_kw)


class FormView(APIView):

    title: str = ""
    description: str = ""
    action: str = ""
    method: str = "POST"
    triggers: Triggers = Triggers()
    schema: dict
    model: pydantic.BaseModel


    @template(TEMPLATES["registration_form.pt"], layout_name="default", raw=False)
    def GET(self, request: Request):
        form = self.setupForm()
        return {"form": form, "view": self, "error": None, "path": request.route.path}

    @template(TEMPLATES["registration_form.pt"], layout_name="default", raw=False)
    def POST(self, request: Request):

        for trigger_id in self.triggers.keys():
            if trigger_id in request.extract().get("form", []):
                return self.triggers[trigger_id]["method"](self, request)
        raise KeyError("No action found")
