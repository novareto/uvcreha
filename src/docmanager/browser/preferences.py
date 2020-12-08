from docmanager.browser.layout import template, TEMPLATES
from docmanager.browser.form import FormView, Form
from docmanager.app import browser
from reiter.form import trigger
from docmanager.request import Request
from horseman.http import Multidict
import pydantic
from docmanager.models import User, UserPreferences
import horseman.response
from urllib.parse import parse_qs


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

    def __init__(self, *args, **kwargs):
        self.tabs = {
            "Kontaktdaten": ('name', 'surname', 'birthdate'),
            "Benachrichtigungen": ('messaging_type', 'webpush_subscription', 'webpush_activated'),
            "Datenschutz": ('datenschutz',),
#            "Benachrichtigungen": Account,
        }

    def setupForm(self, model, data={}, formdata=Multidict(), only=None):
        form = Form.from_model(model, only)
        form.process(data=data, formdata=formdata)
        return form

    def get_user_data(self, request):
        return request.user.preferences.dict()

    @trigger("update", "Speichern", css="btn btn-primary", order=1)
    def update(self, request, data):
        data = data.form
        query_string = parse_qs(request.environ['QUERY_STRING'])
        tab = query_string.get('tab', ' ')[0]
        if not tab:
            raise
        form = self.setupForm(UserPreferences, only=self.tabs.get(tab), formdata=data)
        if not form.validate():
            return {
                "form": form,
                "view": self,
                "error": None,
                "path": request.route.path
            }

        user = request.database.bind(User)
        cd = request.user.preferences.dict()
        cd.update(data.dict())
        user.update(request.user.key, preferences=cd)
        flash_messages = request.utilities.get('flash')
        flash_messages.add(body='Ihre Angaben wurden erfolgreich gespeichert.')
        return horseman.response.Response.create(302, headers={'Location': '/'})

    @trigger("abbrechen", "Abbrechen", css="btn btn-secondary", order=20)
    def abbrechen(self, request, data):
        return horseman.response.Response.create(302, headers={'Location': '/'})

    @template(TEMPLATES["my_preferences.pt"], layout_name="default", raw=False)
    def GET(self, request: Request):
        tabs = {k: self.setupForm(UserPreferences, formdata=None, data=self.get_user_data(request), only=v) for (k, v) in self.tabs.items()}
        return dict(request=request, tabs=tabs, view=self)

    @template(TEMPLATES["my_preferences.pt"], layout_name="default", raw=False)
    def POST(self, request: Request, **data):
        request.extract()
        return self.process_action(request)
