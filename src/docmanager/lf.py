import wtforms
import horseman.response

from docmanager.app import application
from docmanager.utils.form import BaseForm, FormView, Triggers
from docmanager.request import Request
from docmanager.layout import template, TEMPLATES


class LoginForm(BaseForm):

    username = wtforms.fields.StringField(
        'Username',
        validators=(wtforms.validators.InputRequired(),)
    )

    password = wtforms.fields.PasswordField(
        'Password',
        validators=(wtforms.validators.InputRequired(),)
    )


@application.routes.register("/reg")
class RegistrationForm(FormView):

    title = "Registration Form"
    description = "Please fill out all details"
    form = LoginForm
    action = "reg"
    triggers = Triggers()

    @triggers.register('speichern', 'Speichern')
    def speichern(view, request, data, files):
        form = view.form(data)
        if not form.validate():
            return form
        auth = request.app.plugins.get('authentication')
        if (user := auth.from_credentials(
                data.to_dict())) is not None:
            auth.remember(request.environ, user)
            print('The login was successful')
            return horseman.response.Response.create(
                302, headers={'Location': '/'})
        return horseman.response.Response.create(
            302, headers={'Location': '/reg'})

    @triggers.register('abbrechen', 'Abbrechen', _class="btn btn-secondary")
    def abbrechen(form, *args):
        pass


@application.routes.register("/edit_pw")
class EditPassword(FormView):

    title = u"Passwort ändern"
    description = u"Hier können Sie Ihr Passwort ändern"
    form = LoginForm
    del form.username
    action = "edit_pw"
    triggers = Triggers()

    @triggers.register('speichern', 'Speichern')
    def speichern(view, request, data, files):
        form = view.form(data)
        if not form.validate():
            return form
        return horseman.response.Response.create(
            302, headers={'Location': "/%s" % self.action})

    @triggers.register('abbrechen', 'Abbrechen', _class="btn btn-secondary")
    def abbrechen(form, *args):
        pass


@application.routes.register(
    "/preferences", methods=['GET'], permissions={'document.view'})
@template(
    template=TEMPLATES["preferences.pt"], layout_name='default', raw=False)
def preferences(request: Request):
    return dict(request=request)
