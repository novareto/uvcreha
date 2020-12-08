from docmanager.browser.layout import template, TEMPLATES
from docmanager.browser.form import FormView, Form
from docmanager.app import browser
from reiter.form import trigger
from docmanager.request import Request
from horseman.http import Multidict
import pydantic
from docmanager.models import User
import horseman.response


class Kontaktdaten(pydantic.BaseModel):
    name: str
    surname: str


class Account(pydantic.BaseModel):
    name: str
    iban: str


@browser.route("/my_preferences")
class MyPreferences(FormView):

    title = "E-Mail Adresse ändern"
    description = "Edit your preferences."
    action = "my_preferences"

    def setupForm(self, model, data={}, formdata=Multidict()):
        form = Form.from_model(model)
        form.process(data=data, formdata=formdata)
        return form

    @trigger("update", "Update", css="btn btn-primary", order=1)
    def update(self, request, data):
        data = data.form
        form = self.setupForm(Kontaktdaten, formdata=data)
        if not form.validate():
            return form

        user = request.database.bind(User)
        cd = request.user.preferences.dict()
        cd.update(data.dict())
        user.update(request.user.key, preferences=cd)
        return horseman.response.reply(200)

    @trigger("abbrechen", "Abbrechen", css="btn btn-secondary", order=20)
    def abbrechen(self, request):
        pass


    @template(TEMPLATES["my_preferences.pt"], layout_name="default", raw=False)
    def GET(self, request: Request):
        contact = self.setupForm(Kontaktdaten)
        account = self.setupForm(Account)

        tabs = {
            "Kontaktdaten": contact,
            "Passwort": account,
            "Datenschutz": contact,
            "Benachrichtigungen": account,
        }
        return dict(request=request, tabs=tabs, view=self)

    @template(TEMPLATES["my_preferences.pt"], layout_name="default", raw=False)
    def POST(self, request: Request, **data):
        request.extract()
        return self.process_action(request)
