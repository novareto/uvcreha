import horseman.response
from reiter.form import trigger
from uvcreha.app import browser
from uvcreha.browser.form import Form, FormView
from uvcreha.request import Request
from uvcreha import contenttypes
from uvcreha.app import events
from uvcreha.events import UserLoggedInEvent


@browser.register("/login")
class LoginForm(FormView):

    title = "Anmelden"
    description = "Bitte tragen Sie hier Ihre Anmeldeinformationen ein"

    @property
    def action(self):
        return self.request.environ["SCRIPT_NAME"] + "/login"

    def setupForm(self, data=None, formdata=None):
        ct = contenttypes.registry["user"]
        form = Form.from_schema(ct.schema, include=("loginname", "password"))
        form.process(data=data, formdata=formdata)
        return form

    @trigger("Speichern", order=1, css="btn btn-primary")
    def login(self, data):
        form = self.setupForm(formdata=data.form)
        if not form.validate():
            return {"form": form}

        auth = self.request.app.utilities.get("authentication")
        if (user := auth.from_credentials(form.data)) is not None:
            auth.remember(self.request.environ, user)
            self.request.app.notify(UserLoggedInEvent(user, request=self.request))
            return self.redirect(self.request.environ["SCRIPT_NAME"] + "/")

        flash_messages = self.request.utilities.get("flash")
        if flash_messages is not None:
            flash_messages.add(body="Failed login.")
        else:
            print("Warning: flash messages utility is not available.")
        return self.redirect(self.request.environ["SCRIPT_NAME"] + "/")

    @trigger("Abbrechen", css="btn btn-secondary")
    def cancel(form, *args):
        pass


@browser.register("/edit_pw")
class EditPassword(FormView):

    title = "Passwort ändern"
    description = "Hier können Sie Ihr Passwort ändern"
    action = "edit_pw"

    def setupForm(self, data=None, formdata=None):
        ct = contenttypes.registry["user"]
        form = Form.from_schema(ct.schema, include=("password"))
        form.process(data=data, formdata=formdata)
        return form

    @trigger("Speichern", order=1)
    def speichern(self, request, data):
        form = self.setupForm(formdata=data.form)
        if not form.validate():
            return {"form": form}

        ct = contenttypes.registry["user"]
        um = request.database.bind(ct)
        um.update(key=request.user.id, **data.form)
        flash_messages = request.utilities.get("flash")
        flash_messages.add(
            body="Ihr neues Passwort wurde erfolgreich im System gespeichert."
        )
        return self.redirect("/%s" % self.action)

    @trigger("Abbrechen", css="btn btn-secondary")
    def abbrechen(self, *args):
        pass


@browser.register("/logout")
def LogoutView(request: Request):
    auth = request.app.utilities.get("authentication")
    auth.forget(request.environ)
    return horseman.response.Response(302, headers={"Location": "/"})
