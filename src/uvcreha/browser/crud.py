import horseman.response
from horseman.http import Multidict
from pydantic import BaseModel
from typing import ClassVar, Type, Optional, Iterable
from wtforms_pydantic import model_fields
from reiter.form import trigger
from uvcreha.browser.form import FormView, Form


class ModelForm(FormView):
    title: str
    model: ClassVar[Type[BaseModel]]
    readonly: Optional[Iterable[str]] = None

    @property
    def action(self):
        return (
            self.request.environ['SCRIPT_NAME'] +
            self.request.route.path
        )

    @property
    def destination(self):
        return self.request.environ['SCRIPT_NAME'] + '/'

    def fields(self, exclude=(), only=()):
        return model_fields(self.model, exclude=exclude, only=only)

    def get_fields(self):
        # Exclude the pure Arango fields.
        # Exclude the workflow state.
        return self.fields(
            exclude=('key', 'id', 'rev', 'creation_date', 'state')
        )

    def get_initial_data(self):
        return {}

    def setupForm(self, data=None, formdata=Multidict()):
        if data is None:
            data = self.get_initial_data()
        fields = self.get_fields()
        form = Form.from_fields(fields)
        form.process(data=data, formdata=formdata)
        if self.readonly is not None:
            form.readonly(self.readonly)
        return form


class AddForm(ModelForm):

    @trigger("speichern", "Speichern", css="btn btn-primary")
    def speichern(self, request, data):
        form = self.setupForm(formdata=data.form)
        if not form.validate():
            return {'form': form}
        file, response = request.database(self.model).create(
            **{**self.params, **data.form.dict()}
        )
        return horseman.response.redirect(self.destination)


class DefaultView(ModelForm):

    readonly = ...  # represents ALL

    def get_initial_data(self):
        context = self.request.database(self.model).find_one(**self.params)
        return context.dict()

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
        user, response = request.database(self.model).update(
            **{**self.params, **data.form.dict()}
        )
        return horseman.response.redirect(self.destination)

    @trigger("delete", "Delete", css="btn btn-danger")
    def delete(self, request, data):
        request.database(self.model).delete(key=self.context.key)
        return horseman.response.redirect(self.destination)
