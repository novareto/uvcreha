from uvcreha.app import browser
from uvcreha.browser.form import FormView, FormMeta
from horseman.http import Multidict
import horseman.response
from uvcreha.models import User
import wtforms
from reiter.form import trigger


def user_totp_validator(username):

    def validate_totp(form, field):
        totp = browser.utilities['totp']
        if not totp.challenge(field.data, username):
            raise wtforms.ValidationError('Invalid token.')

    return validate_totp


class TwoFAVerification(wtforms.form.Form):

    Meta = FormMeta

    def validate_name(form, field):

        if len(field.data) > 50:
            raise ValidationError('Name must be less than 50 characters')


@browser.route("/2FA")
class TwoFA(FormView):

    @property
    def action(self):
        return self.request.environ['SCRIPT_NAME'] + '/2FA'

    def setupForm(self, data={}, formdata=Multidict()):
        form = wtforms.form.BaseForm({
            'token': wtforms.fields.StringField('Token', [
                user_totp_validator(self.request.user.loginname)
            ])
        })
        form.process(data=data, formdata=formdata)
        return form

    def GET(self):
        form = self.setupForm()
        return {'form': form}

    @trigger("validate", "Validate", css="btn btn-primary")
    def validate(self, request, data):
        form = self.setupForm(formdata=data.form)
        if not form.validate():
            return {'form': form}

        auth = request.app.utilities.get("authentication")
        auth.validate_twoFA(self.request.environ)
        return horseman.response.redirect('/')

    @trigger("request", "Request token", css="btn btn-primary")
    def request_token(self, request, data):
        token = request.app.utilities['totp'].generate(
            request.user.loginname)
        print(token)
        form = self.setupForm()
        return {'form': form}
