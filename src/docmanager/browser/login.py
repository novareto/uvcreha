import pydantic
import horseman.response

from docmanager import db
from docmanager.app import browser
from docmanager.models import User
from docmanager.request import Request
from docmanager.browser.form import Form, FormView, Triggers
from docmanager.browser.layout import template, TEMPLATES
from horseman.http import Multidict


@browser.route("/login", methods=("GET", "POST"))
class LoginForm(FormView):

    title: str = "Registration Form"
    description: str = "Please fill out all details"
    action: str = "login"
    model: pydantic.BaseModel = User
    triggers: Triggers = Triggers()

    def setupForm(self, data={}, formdata=Multidict()):
        form = Form.from_model(self.model, only=("username", "password"))
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
        form = Form.from_model(self.model, only=("password"))
        form.process(data=data, formdata=formdata)
        return form

    @triggers.register("speichern", "Speichern")
    def speichern(view, request):
        data = request.extract()["form"]
        form = view.setupForm(formdata=data)
        if not form.validate():
            return form
        um = db.User(request.app.database.session)
        data.pop('trigger.speichern')
        um.update(key=request.user.key, **data)
        flash_messages = request.utilities.get('flash')
        flash_messages.add(body='Password Change Successful.')
        return horseman.response.Response.create(
            302, headers={"Location": "/%s" % view.action}
        )

    @triggers.register("abbrechen", "Abbrechen", _class="btn btn-secondary")
    def abbrechen(form, *args):
        pass


@browser.route("/edit_mail", permissions={"document.view"})
class EditMail(FormView):

    title = "E-Mail Adresse ändern"
    description = "Hier können Sie Ihre E-Mail Adresse ändern"
    action = "edit_mail"
    triggers = Triggers()
    model: pydantic.BaseModel = User

    def setupForm(self, data={}, formdata=Multidict()):
        form = Form.from_model(self.model, only=("email"))
        form.process(data=data, formdata=formdata)
        return form

    @triggers.register("speichern", "Speichern")
    def speichern(view, request):
        data = request.extract()["form"]
        form = view.setupForm(formdata=data)
        if not form.validate():
            return form
        um = db.User(request.app.database.session)
        data.pop('trigger.speichern')
        um.update(key=request.user.key, **data.dict())
        flash_messages = request.utilities.get('flash')
        flash_messages.add(body='EMAIL Change Successful.')
        return horseman.response.Response.create(
            302, headers={"Location": "/"}
        )

    @triggers.register("abbrechen", "Abbrechen", _class="btn btn-secondary")
    def abbrechen(form, *args):
        pass


@browser.route("/preferences", methods=["GET"], permissions={"document.view"})
@template(TEMPLATES["preferences.pt"], layout_name="default", raw=False)
def preferences(request: Request):
    return dict(request=request)


@browser.route('/logout')
def LogoutView(request: Request):
    request.session.store.clear(request.session.sid)
    return horseman.response.Response.create(
            302, headers={'Location': '/'})
