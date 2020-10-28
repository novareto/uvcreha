import wtforms
import horseman.response

from docmanager.app import ROUTER
from docmanager.utils.form import BaseForm, FormView, Triggers
from docmanager.request import Request


class LoginForm(BaseForm):

    username = wtforms.fields.StringField(
        'Username',
        validators=(wtforms.validators.InputRequired(),)
    )

    password = wtforms.fields.PasswordField(
        'Password',
        validators=(wtforms.validators.InputRequired(),)
    )


@ROUTER.register("/reg")
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
