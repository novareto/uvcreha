import horseman.response

from docmanager import models
from docmanager.app import browser
from docmanager.models import User
from docmanager.request import Request
from reiter.form import trigger
from docmanager.browser.form import Form, FormView
from docmanager.browser.layout import template, TEMPLATES
from horseman.http import Multidict


@browser.route("/login")
class LoginForm(FormView):

    title = "Anmelden"
    description = "Bitte tragen Sie hier Ihre Anmeldeinformationen ein"
    action = "login"
    model = models.User

    def setupForm(self, data={}, formdata=Multidict()):
        form = Form.from_model(self.model, only=("username", "password"))
        form.process(data=data, formdata=formdata)
        return form

    @trigger("speichern", "Speichern", order=1)
    def login(self, request, data):
        form = self.setupForm(formdata=data.form)
        if not form.validate():
            return {
                "form": form,
                "view": self,
                "error": None,
                "path": request.route.path
            }

        auth = request.app.utilities.get("authentication")
        if (user := auth.from_credentials(data.form.dict())) is not None:
            auth.remember(request.environ, user)
            return horseman.response.Response.create(
                302, headers={"Location": "/"}
            )
        flash_messages = request.utilities.get('flash')
        flash_messages.add(body='Failed login.')
        return horseman.response.Response.create(
            302, headers={"Location": "/login"}
        )

    @trigger("abbrechen", "Abbrechen", css="btn btn-secondary")
    def cancel(form, *args):
        pass


@browser.route("/edit_pw")
class EditPassword(FormView):

    title = "Passwort ändern"
    description = "Hier können Sie Ihr Passwort ändern"
    action = "edit_pw"
    model = User

    def setupForm(self, data={}, formdata=Multidict()):
        form = Form.from_model(self.model, only=("password"))
        form.process(data=data, formdata=formdata)
        return form

    @trigger("speichern", "Speichern", order=1)
    def speichern(view, request, data):
        form = view.setupForm(formdata=data.form)
        if not form.validate():
            return form

        um = request.database(User)
        um.update(key=request.user.key, **data.form)
        flash_messages = request.utilities.get('flash')
        flash_messages.add(
            body='Ihr neues Passwort wurde erfolgreich im System gespeichert.')
        return horseman.response.Response.create(
            302, headers={"Location": "/%s" % view.action}
        )

    @trigger("abbrechen", "Abbrechen", css="btn btn-secondary")
    def abbrechen(form, *args):
        pass


@browser.route("/edit_mail", permissions={"document.view"})
class EditMail(FormView):

    title = "E-Mail Adresse ändern"
    description = "Hier können Sie Ihre E-Mail Adresse ändern"
    action = "edit_mail"
    model = User

    def setupForm(self, data={}, formdata=Multidict()):
        form = Form.from_model(self.model, only=("email"))
        form.process(data=data, formdata=formdata)
        return form

    @template(TEMPLATES["base_form.pt"], layout_name="default", raw=False)
    def GET(self, request: Request):
        userdata = request.user.dict()
        form = self.setupForm(data=userdata)
        return {
            "form": form,
            "view": self,
            "error": None,
            "path": request.route.path
        }

    @trigger("abbrechen", "Abbrechen", css="btn btn-secondary")
    def abbrechen(form, request, data):
        flash_messages = request.utilities.get('flash')
        flash_messages.add(
            body=('Ihre E-Mail Adresse wurde erfolgreich im '
                  'System gespeichert.'))
        return horseman.response.Response.create(
            302, headers={"Location": "/"}
        )

    @trigger("speichern", "Speichern")
    def speichern(view, request, data):
        form = view.setupForm(formdata=data.form)
        if not form.validate():
            return form
        um = request.database.bind(models.User)
        um.update(key=request.user.key, **data.form.dict())
        flash_messages = request.utilities.get('flash')
        flash_messages.add(
            body=('Ihre E-Mail Adresse wurde erfolgreich im '
                  'System gespeichert.'))
        return horseman.response.Response.create(
            302, headers={"Location": "/"}
        )


@browser.route(
    "/user_preferences", methods=["GET"], permissions={"document.view"})
@template(TEMPLATES["preferences.pt"], layout_name="default", raw=False)
def preferences(request: Request):
    return dict(request=request)


@browser.route('/logout')
def LogoutView(request: Request):
    request.session.store.clear(request.session.sid)
    return horseman.response.Response.create(
            302, headers={'Location': '/'})
