import wtforms
import horseman.response

from docmanager.app import application
from docmanager.utils.form import FormView, Triggers
from docmanager.request import Request
from docmanager.layout import template, TEMPLATES
#from docmanager.utils.flashmessages import Message


class Schema(dict):

    def omit(self, *args):
        return self.__class__(
            {k: v for k, v in self.items() if k not in args})

    def select(self, *args):
        return self.__class__(
            {k: v for k, v in self.items() if k in args})


LoginSchema = Schema(
    username = wtforms.fields.StringField(
        'Username',
        validators=(wtforms.validators.InputRequired(),)),

    password = wtforms.fields.PasswordField(
        'Password',
        validators=(wtforms.validators.InputRequired(),))
)


@application.routes.register("/reg")
class RegistrationForm(FormView):

    title: str = "Registration Form"
    description: str = "Please fill out all details"
    schema: Schema = LoginSchema
    action: str = "reg"
    triggers: Triggers = Triggers()

    @triggers.register(
        'speichern', 'Speichern')
    def speichern(view, request):
        form = view.setupForm(formdata=request.data['form'])
        if not form.validate():
            return form

        auth = request.app.plugins.get('authentication')
        if (user := auth.from_credentials(
                request.data['form'].to_dict())) is not None:
            auth.remember(request.environ, user)
            #request.flash = Message(type='info', body="Sie sind nun angemeldet!")
            return horseman.response.Response.create(
                302, headers={'Location': '/'})
        return horseman.response.Response.create(
            302, headers={'Location': '/reg'})

    @triggers.register(
        'abbrechen', 'Abbrechen', _class="btn btn-secondary")
    def abbrechen(form, *args):
        pass


@application.routes.register("/edit_pw")
class EditPassword(FormView):

    title = u"Passwort ändern"
    description = u"Hier können Sie Ihr Passwort ändern"
    schema = LoginSchema.omit('username')
    action = "edit_pw"
    triggers = Triggers()

    @triggers.register('speichern', 'Speichern')
    def speichern(view, request, data, files):
        form = view.setupForm(formdata=data)
        if not form.validate():
            return dict(form=form, view=view)
        import pdb; pdb.set_trace()
        return horseman.response.Response.create(
            302, headers={'Location': "/%s" % view.action})

    @triggers.register(
        'abbrechen', 'Abbrechen', _class="btn btn-secondary")
    def abbrechen(form, *args):
        pass


@application.routes.register(
    "/preferences", methods=['GET'], permissions={'document.view'})
@template(
    template=TEMPLATES["preferences.pt"], layout_name='default', raw=False)
def preferences(request: Request):
    return dict(request=request)
