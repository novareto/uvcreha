"""Database agnostic CRUD.
"""

import horseman.response
from horseman.http import Multidict
from typing import ClassVar, Type, Optional, Iterable, Callable, Dict, Any
from reiter.form import trigger
from uvcreha.browser.form import FormView
from uvcreha.contenttypes import Content


class BaseForm(FormView):
    title: str
    readonly: Optional[Iterable[str]] = None
    hook: Optional[Callable] = None

    @property
    def action(self):
        return (
            self.request.environ['SCRIPT_NAME'] +
            self.request.route.path
        )

    @property
    def destination(self):
        return self.request.environ['SCRIPT_NAME'] + '/'

    def get_form(self):
        raise NotImplementedError('Implement your own.')

    def get_initial_data(self):
        return {}

    def setupForm(self, data=None, formdata=Multidict()):
        form = self.get_form()
        if data is None:
            data = self.get_initial_data()
        form.process(data=data, formdata=formdata)
        if self.readonly is not None:
            form.readonly(self.readonly)
        return form


class AddForm(BaseForm):

    def get_initial_data(self):
        return self.params

    def create(self, data):
        raise NotImplementedError('implement in your subclass')

    @trigger("speichern", "Speichern", css="btn btn-primary")
    def speichern(self, request, data):
        form = self.setupForm(formdata=data.form)
        if not form.validate():
            return {'form': form}
        obj = self.create(data)
        if self.hook is not None:
            self.hook(obj)
        return horseman.response.redirect(self.destination)


class DefaultView(BaseForm):

    readonly = ...  # represents ALL

    def get_initial_data(self):
        raise NotImplementedError('implement in your subclass')

    def GET(self):
        form = self.setupForm()
        return {'form': form}


class EditForm(BaseForm):

    def get_initial_data(self):
        raise NotImplementedError('implement in your subclass')

    def apply(self, data: Dict):
        raise NotImplementedError('implement in your subclass')

    def remove(self, key: Any):
        raise NotImplementedError('implement in your subclass')

    @trigger("speichern", "Speichern", css="btn btn-primary")
    def speichern(self, request, data):
        form = self.setupForm(formdata=data.form)
        if not form.validate():
            return {'form': form}
        obj = self.apply(data)
        if self.hook is not None:
            self.hook(obj)
        return horseman.response.redirect(self.destination)

    @trigger("delete", "Delete", css="btn btn-danger")
    def delete(self, request, data):
        self.remove(self.context.metadata.id)
        return horseman.response.redirect(self.destination)
