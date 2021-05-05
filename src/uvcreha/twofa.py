from horseman.http import Multidict
from reiter.form import trigger
from uvcreha.app import browser
from uvcreha.browser.form import FormMeta, FormView, FormMeta
from uvcreha.models import User
import horseman.response
import wtforms


def user_totp_validator(totp):

    def validate_totp(form, field):
        if not totp.verify(field.data, valid_window=1):
            raise wtforms.ValidationError('Invalid token.')

    return validate_totp


@browser.route("/2FA")
class TwoFA(FormView):

    title = "Überprüfung"
    description = "Bitte geben Sie Ihre SMS TAN ein"

    @property
    def action(self):
        return self.request.environ['SCRIPT_NAME'] + '/2FA'

    def setupForm(self, data={}, formdata=Multidict()):
        form = wtforms.form.BaseForm({
            'token': wtforms.fields.StringField('Token', [
                user_totp_validator(self.request.user.TOTP)
            ])
        }, meta=FormMeta())
        form.process(data=data, formdata=formdata)
        return form

    def GET(self):
        form = self.setupForm()
        token = self.request.user.TOTP.now()
        print(token)
        return {'form': form}


    @trigger("validate", "Überprüfen", css="btn btn-primary")
    def validate(self, request, data):
        form = self.setupForm(formdata=data.form)
        if not form.validate():
            return {'form': form}

        auth = request.app.utilities.get("authentication")
        auth.validate_twoFA(self.request.environ)
        return horseman.response.redirect('/')

    @trigger("request", "Neuen Key anfordern", css="btn btn-primary")
    def request_token(self, request, data):
        token = request.user.TOTP.now()
        print(token)
        form = self.setupForm()
        return {'form': form}
