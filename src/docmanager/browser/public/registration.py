import pydantic
import horseman.response

from docmanager.app import application
from docmanager.models import User
from docmanager.request import Request
from docmanager.browser.form import FormView, Triggers
from docmanager.browser.layout import template, TEMPLATES


@application.routes.register("/reg")
class RegistrationForm(FormView):

    title: str = "Registration Form"
    description: str = "Please fill out all details"
    action: str = "reg"
    model: pydantic.BaseModel = User
    triggers: Triggers = Triggers()

    @triggers.register("speichern", "Speichern")
    def speichern(view, request):
        data = request.extract()["form"]
        form = view.setupForm(formdata=data)
        if not form.validate():
            return form

        auth = request.app.plugins.get("authentication")
        if (user := auth.from_credentials(data.dict())) is not None:
            auth.remember(request.environ, user)
            # request.flash = Message(type='info', body="Sie sind nun angemeldet!")
            return horseman.response.Response.create(302, headers={"Location": "/"})
        return horseman.response.Response.create(302, headers={"Location": "/reg"})

    @triggers.register("abbrechen", "Abbrechen", _class="btn btn-secondary")
    def abbrechen(form, *args):
        pass


@application.routes.register("/edit_pw")
class EditPassword(FormView):

    title = "Passwort ändern"
    description = "Hier können Sie Ihr Passwort ändern"
    action = "edit_pw"
    triggers = Triggers()
    model: pydantic.BaseModel = User

    @triggers.register("speichern", "Speichern")
    def speichern(view, request, data, files):
        form = view.setupForm(formdata=data)
        if not form.validate():
            return dict(form=form, view=view)
        print('DO SOME REAL STUFF HERE')
        return horseman.response.Response.create(
            302, headers={"Location": "/%s" % view.action}
        )

    @triggers.register("abbrechen", "Abbrechen", _class="btn btn-secondary")
    def abbrechen(form, *args):
        pass


@application.routes.register(
    "/preferences", methods=["GET"], permissions={"document.view"}
)
@template(template=TEMPLATES["preferences.pt"], layout_name="default", raw=False)
def preferences(request: Request):
    return dict(request=request)
