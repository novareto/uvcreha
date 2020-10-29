import wtforms
import collections
from horseman.meta import APIView
from docmanager.layout import template, TEMPLATES
from docmanager.request import Request
from horseman.parsing import parse
from horseman.http import Multidict


class Triggers(collections.OrderedDict):

    def register(self, name, title=None, _class='btn btn-primary'):
        def add_trigger(method):
            tid = f'trigger.{name}'
            self[tid] = {
                'id': tid,
                'title': title or name,
                'method': method,
                'class': _class
                }
            return method
        return add_trigger


class FormView(APIView):

    title: str = ""
    description: str = ""
    action: str = ""
    method: str = "POST"
    triggers: Triggers = Triggers()
    schema: dict

    class Meta(wtforms.meta.DefaultMeta):
        def render_field(inst, field, render_kw):
            class_ = 'form-control'
            if field.errors:
                class_ += ' is-invalid'
            render_kw.update({'class_': class_})
            return field.widget(field, **render_kw)

    def setupForm(self, data={}, formdata=Multidict()):
        form = wtforms.form.BaseForm(self.schema, meta=self.Meta())
        form.process(data=data, formdata=formdata)
        return form

    @template(
        TEMPLATES['registration_form.pt'], layout_name='default', raw=False)
    def GET(self, request: Request):
        form = self.setupForm()
        return {
            'form': form,
            'view': self,
            'error': None,
            'path': request.route.path
        }

    @template(
        TEMPLATES['registration_form.pt'], layout_name='default', raw=False)
    def POST(self, request: Request):
        request.environ['wsgi.input'].seek(0)
        data, files = parse(
            request.environ['wsgi.input'], request.content_type)
        for trigger_id in self.triggers.keys():
            if trigger_id in data:
                return self.triggers[trigger_id]['method'](
                    self, request, data, files)
        raise KeyError('No action found')
