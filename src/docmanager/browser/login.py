import horseman.response

from docmanager import models
from docmanager.app import browser
from docmanager.models import User
from docmanager.request import Request
from reiter.form import trigger
from docmanager.browser.form import Form, FormView
from docmanager.browser.layout import TEMPLATES
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
            return {"form": form}

        auth = request.app.utilities.get("authentication")
        if (user := auth.from_credentials(data.form.dict())) is not None:
            auth.remember(request.environ, user)
            return self.redirect("/")

        flash_messages = request.utilities.get('flash')
        flash_messages.add(body='Failed login.')
        return self.redirect("/")

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
    def speichern(self, request, data):
        form = self.setupForm(formdata=data.form)
        if not form.validate():
            return {"form": form}

        um = request.database(User)
        um.update(key=request.user.key, **data.form)
        flash_messages = request.utilities.get('flash')
        flash_messages.add(
            body='Ihr neues Passwort wurde erfolgreich im System gespeichert.')
        return self.redirect("/%s" % self.action)

    @trigger("abbrechen", "Abbrechen", css="btn btn-secondary")
    def abbrechen(self, *args):
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

    def GET(self, request: Request):
        userdata = request.user.dict()
        form = self.setupForm(data=userdata)
        return {"form": form}

    @trigger("abbrechen", "Abbrechen", css="btn btn-secondary")
    def abbrechen(self, request, data):
        flash_messages = request.utilities.get('flash')
        flash_messages.add(
            body=('Ihre E-Mail Adresse wurde erfolgreich im '
                  'System gespeichert.'))
        return self.redirect("/")

    @trigger("speichern", "Speichern")
    def speichern(self, request, data):
        form = self.setupForm(formdata=data.form)
        if not form.validate():
            return self.namespace(form=form, error=None)
        um = request.database.bind(models.User)
        um.update(key=request.user.key, **data.form.dict())
        flash_messages = request.utilities.get('flash')
        flash_messages.add(
            body=('Ihre E-Mail Adresse wurde erfolgreich im '
                  'System gespeichert.'))
        return self.redirect("/")


@browser.route(
    "/user_preferences", methods=["GET"], permissions={"document.view"})
def preferences(request: Request):
    return request.app.ui.response(
        TEMPLATES["preferences.pt"],
        request=request
    )


@browser.route('/logout')
def LogoutView(request: Request):
    request.session.store.clear(request.session.sid)
    return horseman.response.Response.create(
            302, headers={'Location': '/'})
