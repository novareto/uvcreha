import pydantic
from urllib.parse import parse_qs
from horseman.response import Response
from horseman.http import Multidict
from reiter.form import trigger
from uvcreha.app import browser
from uvcreha.browser.form import FormView, Form
from uvcreha.browser.layout import TEMPLATES
from uvcreha.models import User, UserPreferences
from uvcreha.request import Request
from uvcreha.workflow import user_workflow
from uvcreha.browser.composed import ComposedView
from reiter.view.meta import View

from pydantic import BaseModel
from uvcreha.browser.form import FormView
from reiter.form import trigger


@browser.route("/preferences")
class ComposedDocument(ComposedView):
    title = "Einstellungen"
    description = "Beschreibung"


@ComposedDocument.pages.component('default')
class DefaultView(View):
    title = 'Einstellungen'

    def GET(self):
        return 'Auf den Tabs hier haben Sie die Möglichkeit Einstellungen vorzunehmen'


@ComposedDocument.pages.component('stammdaten')
class Stammdaten(FormView):
    title = 'Stammedaten'
    description = "Stammdaten"
    model = UserPreferences


    def setupForm(self, data={}, formdata=Multidict()):
        form = Form.from_model(self.model, only=('name', 'surname', 'birthdate'))
        form.process(data=data, formdata=formdata)
        return form

    @property
    def action(self):
        return (
            self.request.environ['SCRIPT_NAME'] +
            self.request.route.path + '?page=stammdaten'
        )

    @trigger(title="Speichern", id="save", css="btn btn-primary")
    def handle_save(self, request, data):
        form = self.setupForm(formdata=data.form)
        if not form.validate():
            return {"form": form}
        binding = self.request.database(User)
        binding.update(self.request.user.key, preferences=data.form.dict())
        return {"form": form}


@ComposedDocument.pages.component('email')
class EMail(FormView):
    title = 'E-Mail'
    description = "EMail-Adresse"
    model = User 

    def setupForm(self, data={}, formdata=Multidict()):
        form = Form.from_model(self.model, only=('email',))
        data['email'] = self.request.user.email
        form.process(data=data, formdata=formdata)
        return form

    @property
    def action(self):
        return (
            self.request.environ['SCRIPT_NAME'] +
            self.request.route.path + '?page=email'
        )

    @trigger(title="Speichern", id="save", css="btn btn-primary")
    def handle_save(self, request, data):
        form = self.setupForm(formdata=data.form)
        if not form.validate():
            return {"form": form}
        binding = self.request.database(self.model)
        binding.update(self.request.user.key, **data.form.dict())
        self.request.utilities['flash'].add('Ihre E-Mail Adresse wurde geändert')
        return {"form": form}


@ComposedDocument.pages.component('password')
class Password(FormView):
    title = 'Passwort'
    description = "Passwort"
    model = User 

    def setupForm(self, data={}, formdata=Multidict()):
        form = Form.from_model(self.model, only=('password',))
        form.process(data=data, formdata=formdata)
        return form

    @property
    def action(self):
        return (
            self.request.environ['SCRIPT_NAME'] +
            self.request.route.path + '?page=password'
        )

    @trigger(title="Speichern", id="save", css="btn btn-primary")
    def handle_save(self, request, data):
        form = self.setupForm(formdata=data.form)
        if not form.validate():
            return {"form": form}
        binding = self.request.database(self.model)
        binding.update(self.request.user.key, **data.form.dict())
        self.request.utilities['flash'].add('Ihr Passwort wurde erfolgreich geändert')
        return {"form": form}


@ComposedDocument.pages.component('benachrichtigungen')
class Notifications(FormView):
    title = 'Benachrichtigungen'
    description = "Benachrichtigungen"
    model = UserPreferences

    def setupForm(self, data={}, formdata=Multidict()):
        form = Form.from_model(self.model, only=('messaging_type',))
        form.process(data=data, formdata=formdata)
        return form

    @property
    def action(self):
        return (
            self.request.environ['SCRIPT_NAME'] +
            self.request.route.path + '?page=benachrichtigungen'
        )

    @trigger(title="Speichern", id="save", css="btn btn-primary")
    def handle_save(self, request, data):
        form = self.setupForm(formdata=data.form)
        if not form.validate():
            return {"form": form}
        binding = self.request.database(User)
        binding.update(self.request.user.key, preferences=data.form.dict())
        self.request.utilities['flash'].add('Ihr Passwort wurde erfolgreich geändert')
        return {"form": form}


@browser.route("/register")
class RegistrationForm(FormView):

    title = "Registration"
    description = "Finish your registration"
    action = "/register"
    model = User

    def setupForm(self, data={}, formdata=Multidict()):
        form = Form.from_model(
            self.model, only=("email",), email={"required": True})
        form.process(data=data, formdata=formdata)
        return form

    @trigger("register", "Register", css="btn btn-primary")
    def register(self, request, data):
        form = self.setupForm(data=request.user.dict(), formdata=data.form)
        if not form.validate():
            return {"form": form}

        request.user.email = form.data["email"]
        wf = user_workflow(request.user)
        wf.state = user_workflow.states.active
        request.database.save(request.user)
        return self.redirect("/")
