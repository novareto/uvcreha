import pydantic
import horseman.response

from docmanager.app import browser
from docmanager.models import User
from docmanager.request import Request
from docmanager.browser.form import CustomBaseForm, FormView, Triggers
from docmanager.browser.layout import template, TEMPLATES
from horseman.http import Multidict
from wtforms_pydantic.wtforms_pydantic import model_form


@browser.route("/login", methods=("GET", "POST"))
class RegistrationForm(FormView):

    title: str = "Registration Form"
    description: str = "Please fill out all details"
    action: str = "login"
    model: pydantic.BaseModel = User
    triggers: Triggers = Triggers()

    def setupForm(self, data={}, formdata=Multidict()):
        form = model_form(
            self.model,
            base_class=CustomBaseForm,
            only=("username", "password")
        )()
        form.process(data=data, formdata=formdata)
        return form

    @triggers.register("speichern", "Speichern")
    def login(view, request):
        data = request.extract()["form"]
        form = view.setupForm(formdata=data)
        if not form.validate():
            return form

        auth = request.app.plugins.get("authentication")
        if (user := auth.from_credentials(data.dict())) is not None:
            auth.remember(request.environ, user)
            return horseman.response.Response.create(
                302, headers={"Location": "/"}
            )
        flash_messages = request.utilities.get('flash')
        flash_messages.add(body='Failed login.')
        return horseman.response.Response.create(
            302, headers={"Location": "/login"}
        )

    @triggers.register("abbrechen", "Abbrechen", _class="btn btn-secondary")
    def cancel(form, *args):
        pass


@browser.route("/edit_pw")
class EditPassword(FormView):

    title = "Passwort ändern"
    description = "Hier können Sie Ihr Passwort ändern"
    action = "edit_pw"
    triggers = Triggers()
    model: pydantic.BaseModel = User

    def setupForm(self, data={}, formdata=Multidict()):
        form = model_form(
            self.model, base_class=CustomBaseForm, only=("password"))()
        form.process(data=data, formdata=formdata)
        return form

    @triggers.register("speichern", "Speichern")
    def speichern(view, request):
        data = request.extract()["form"]
        form = view.setupForm(formdata=data)
        if not form.validate():
            return form
        print("DO SOME REAL STUFF HERE")
        return horseman.response.Response.create(
            302, headers={"Location": "/%s" % view.action}
        )

    @triggers.register("abbrechen", "Abbrechen", _class="btn btn-secondary")
    def abbrechen(form, *args):
        pass


@browser.route(
    "/preferences", methods=["GET"], permissions={"document.view"}
)
@template(TEMPLATES["preferences.pt"], layout_name="default", raw=False)
def preferences(request: Request):
    return dict(request=request)


@browser.route('/logout')
def LogoutView(request: Request):
    request.session.store.clear(request.session.sid)
    return horseman.response.Response.create(
            302, headers={'Location': '/'})
