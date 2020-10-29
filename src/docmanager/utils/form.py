import wtforms
import collections
from horseman.meta import APIView
from docmanager.layout import template, TEMPLATES
from docmanager.request import Request
from horseman.parsing import parse


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
    form: wtforms.Form

    def setupForm(self):
        return self.form() 

    @template(TEMPLATES['registration_form.pt'], layout_name='default', raw=False)
    def GET(self, request: Request):
        form = self.setupForm()
        import pdb; pdb.set_trace()
        return {
            'form': form,
            'view': self,
            'error': None,
            'path': request.route.path
        }

    @template(TEMPLATES['registration_form.pt'], layout_name='default', raw=False)
    def POST(self, request: Request):
        if request.method == "POST":
            request.environ['wsgi.input'].seek(0)
            data, files = parse(
                request.environ['wsgi.input'], request.content_type)
            for trigger_id in self.triggers.keys():
                if trigger_id in data:
                    return self.triggers[trigger_id]['method'](
                        self, request, data, files)
            raise KeyError('No action found')
        return {'form': form, 'error': 'auth', 'path': request.route.path}


class BaseForm(wtforms.Form):

    class Meta:
        def render_field(self, field, render_kw):
            class_ = 'form-control'
            if field.errors:
                class_ += ' is-invalid'
            render_kw.update({'class_': class_})
            return field.widget(field, **render_kw)
