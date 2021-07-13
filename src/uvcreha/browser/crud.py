"""Database agnostic CRUD.
"""

from abc import abstractmethod
from typing import Optional, Iterable, Dict, Any

import horseman.response
from reiter.form import trigger
from uvcreha.browser.form import FormView
from uvcreha import events


class BaseForm(FormView):
    title: str
    readonly: Optional[Iterable[str]] = None

    @property
    def action(self):
        return self.request.environ["SCRIPT_NAME"] + self.request.route.path

    @property
    def destination(self):
        return self.request.environ["SCRIPT_NAME"] + "/"

    @abstractmethod
    def get_form(self):
        raise NotImplementedError("Implement your own.")

    def get_initial_data(self):
        return {}

    def setupForm(self, data=None, formdata=None):
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

    @abstractmethod
    def create(self, data):
        """Created the object in the DB"""

    @trigger("Speichern", css="btn btn-primary")
    def speichern(self, request, data):
        form = self.setupForm(formdata=data.form)
        if not form.validate():
            return {"form": form}
        obj = self.create(form.data)
        request.app.notify(events.ObjectCreatedEvent(self.request, obj))
        return horseman.response.redirect(self.destination)


class DefaultView(BaseForm):

    readonly = ...  # represents ALL

    @abstractmethod
    def get_initial_data(self):
        pass

    def GET(self):
        form = self.setupForm()
        return {"form": form}


class EditForm(BaseForm):

    @abstractmethod
    def get_initial_data(self):
        pass

    @abstractmethod
    def apply(self, data: Dict):
        pass

    @abstractmethod
    def remove(self, key: Any):
        pass

    @trigger("Speichern", css="btn btn-primary")
    def speichern(self, request, data):
        form = self.setupForm(formdata=data.form)
        if not form.validate():
            return {"form": form}
        obj = self.apply(form.data)
        request.app.notify(events.ObjectModifiedEvent(self.request, obj))
        return horseman.response.Response.redirect(self.destination)

    @trigger("Delete", css="btn btn-danger")
    def delete(self, request, data):
        self.remove(self.context.id)
        request.app.notify(events.ObjectRemovedEvent(self.request, obj))
        return horseman.response.Response.redirect(self.destination)
