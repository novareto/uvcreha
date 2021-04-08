import horseman.response
from horseman.http import Multidict
from pydantic import BaseModel
from typing import ClassVar, Type, Optional, Iterable, Callable
from wtforms_pydantic import model_fields
from reiter.form import trigger
from uvcreha.browser.form import FormView, Form


class ModelForm(FormView):
    title: str
    model: ClassVar[Type[BaseModel]]
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

    def fields(self, exclude=(), include=()):
        return model_fields(self.model, exclude=exclude, include=include)

    def get_fields(self):
        # Exclude the pure Arango fields.
        # Exclude the workflow state.
        return self.fields(
            exclude=('key', 'id', 'rev', 'creation_date', 'state')
        )

    def get_form(self):
        return Form.from_fields(self.get_fields())

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


class AddForm(ModelForm):

    def get_initial_data(self):
        return self.request.route.params

    @trigger("speichern", "Speichern", css="btn btn-primary")
    def speichern(self, request, data):
        form = self.setupForm(formdata=data.form)
        if not form.validate():
            return {'form': form}
        obj, response = request.database(self.model).create(
            **{**self.params, **data.form.dict()}
        )
        if self.hook is not None:
            self.hook(obj)
        return horseman.response.redirect(self.destination)


class DefaultView(ModelForm):

    readonly = ...  # represents ALL

    def update(self):
        self.context = self.request.database(
            self.model).find_one(**self.params)

    def get_initial_data(self):
        return self.context.dict()

    def GET(self):
        form = self.setupForm()
        return {'form': form}


class EditForm(ModelForm):

    def update(self):
        super().update()
        self.context = self.request.database(
            self.model).find_one(**self.params)

    def get_initial_data(self):
        return self.context.dict()

    @trigger("speichern", "Speichern", css="btn btn-primary")
    def speichern(self, request, data):
        form = self.setupForm(formdata=data.form)
        if not form.validate():
            return {'form': form}
        obj = self.request.database(self.model).update(
            self.context.__key__,
            **{**self.params, **data.form.dict()}
        )
        if self.hook is not None:
            self.hook(obj)
        return horseman.response.redirect(self.destination)

    @trigger("delete", "Delete", css="btn btn-danger")
    def delete(self, request, data):
        request.database(self.model).delete(key=self.context.key)
        return horseman.response.redirect(self.destination)
