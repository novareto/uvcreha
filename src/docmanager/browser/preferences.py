import pydantic
from urllib.parse import parse_qs
from horseman.http import Multidict
from reiter.form import trigger
from docmanager.app import browser
from docmanager.browser.form import FormView, Form
from docmanager.browser.layout import TEMPLATES
from docmanager.models import User, UserPreferences
from docmanager.request import Request
from docmanager.workflow import user_workflow


class Kontaktdaten(pydantic.BaseModel):
    name: str
    surname: str


class Account(pydantic.BaseModel):
    name: str
    iban: str


@browser.route("/preferences")
class MyPreferences(FormView):

    title = "E-Mail Adresse ändern"
    description = "Edit your preferences."
    action = "preferences"

    template = TEMPLATES["my_preferences.pt"]

    def update(self):
        self.tabs = {
            "Stammdaten": ("name", "surname", "birthdate"),
            "Benachrichtigungen": (
                "messaging_type",
                "webpush_subscription",
                "webpush_activated",
            ),
            "Datenschutz": ("datenschutz",),
            "Kontaktdaten": ("email", "mobile"),
        }

    def setupForm(self, model, data={}, formdata=Multidict(), only=None):
        form = Form.from_model(model, only)
        form.process(data=data, formdata=formdata)
        return form

    def get_user_data(self, request):
        if request.user.preferences:
            return request.user.preferences.dict()
        return UserPreferences.construct().dict()

    @trigger("update", "Speichern", css="btn btn-primary", order=1)
    def update_action(self, request, data):
        data = data.form
        query_string = parse_qs(request.environ["QUERY_STRING"])
        tab = query_string.get("tab", " ")[0]
        if not tab:
            raise
        form = self.setupForm(
            UserPreferences, only=self.tabs.get(tab), formdata=data)
        if not form.validate():
            return {"tabs": self.tabs, "form": form}

        user = request.database(User)
        cd = self.get_user_data(request)
        cd.update(data.dict())
        user.update(request.user.key, preferences=cd)
        flash_messages = request.utilities.get("flash")
        flash_messages.add(body=("Ihre Angaben wurden erfolgreich "
                                 "gespeichert."))
        return self.redirect("/")

    @trigger("abbrechen", "Abbrechen", css="btn btn-secondary", order=20)
    def abbrechen(self, request, data):
        return self.redirect("/")

    def GET(self, request: Request):
        return {"tabs": self.tabs}

    def POST(self, request: Request, **data):
        request.extract()
        return self.process_action(request)


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
