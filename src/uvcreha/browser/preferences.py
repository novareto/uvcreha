import pydantic
from urllib.parse import parse_qs
from horseman.response import Response
from horseman.http import Multidict
from reiter.form import trigger
from uvcreha.app import browser
from uvcreha.browser.crud import ModelForm
from uvcreha.browser.form import Composer, FormView, Form
from uvcreha.browser.crud import ModelForm
from uvcreha.browser.layout import TEMPLATES
from uvcreha.models import User, UserPreferences, MessagingType
from uvcreha.request import Request
from uvcreha.workflow import user_workflow
from uvcreha.browser.composed import ComposedView
from reiter.view.meta import View
from pydantic import BaseModel
from uvcreha.browser.form import FormView, MultiCheckboxField
from reiter.form import trigger
from wtforms_pydantic import model_fields


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
        form = Form.from_model(self.model, include=('name', 'surname', 'birthdate'))
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
        form = Form.from_model(self.model, include=('email',))
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
        form = Form.from_model(self.model, include=('password',))
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
class Notifications(ModelForm):
    title = 'Benachrichtigungen'
    description = "Benachrichtigungen"
    model = UserPreferences

    def update(self):
        if self.request.user.preferences is not None:
            self.preferences = self.request.user.preferences
        else:
            self.preferences = self.model.construct()

    def get_fields(self):
        return self.fields(include=('messaging_type',))

    def get_initial_data(self):
        return self.preferences.dict()

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
        self.preferences.messaging_type = form.data['messaging_type']
        binding = self.request.database(User)
        binding.update(
            self.request.user.key, preferences=self.preferences.dict())
        self.request.utilities['flash'].add(
            'Ihr Passwort wurde erfolgreich geändert')
        return {"form": form}


@browser.route("/register")
class RegistrationForm(ModelForm):

    title = "Registrierung"
    description = "Bitte vervollständigen Sie Ihre Registrierung."
    action = "/register"
    model = User


    def update(self):
        self.context = self.request.database(User).find_one(uid=self.request.user.key)
        self.composer = Composer(self.context)

    def get_fields(self):
        return dict(self.composer.fields(
            'email',
            'preferences.datenschutz',
            'preferences.teilnahme'
        ))

    def get_initial_data(self):
        return self.composer.default_values()

    def isetupForm(self, data={}, formdata=Multidict()):
        form = Form.from_model(
            self.model, include=("email",), email={"required": True})
        form.process(data=data, formdata=formdata)
        return form

    @trigger("register", "Register", css="btn btn-primary")
    def register(self, request, data):
        form = self.setupForm(data=request.user.dict(), formdata=data.form)
        if not form.validate():
            return {"form": form}
        request.user.email = form.data["email"]
        request.user.preferences.datenschutz = form.data["preferences.datenschutz"]
        request.user.preferences.teilnahme = form.data["preferences.teilnahme"]
        wf = user_workflow(request.user)
        wf.state = user_workflow.states.active
        request.database.save(request.user)
        return self.redirect("/")
