import base64
import qrcode
import wtforms
from io import BytesIO

import horseman.response
from horseman.http import Multidict
from reiter.form import trigger
from uvcreha.events import TwoFAEvent
from uvcreha.app import browser, ui
from uvcreha.request import Request
from uvcreha.browser.form import FormMeta, FormView


def user_totp_validator(totp):
    def validate_totp(form, field):
        if not totp.verify(field.data, valid_window=1):
            raise wtforms.ValidationError("Invalid token.")

    return validate_totp


@browser.register("/2FA")
class TwoFA(FormView):

    title = "Überprüfung"
    description = "Bitte geben Sie Ihre SMS TAN ein"

    @property
    def action(self):
        return self.request.environ["SCRIPT_NAME"] + "/2FA"

    def setupForm(self, data={}, formdata=Multidict()):
        form = wtforms.form.BaseForm(
            {
                "token": wtforms.fields.StringField(
                    "Token", [user_totp_validator(self.request.user.TOTP)]
                )
            },
            meta=FormMeta(),
        )
        form.process(data=data, formdata=formdata)
        return form

    def GET(self):
        form = self.setupForm()
        token = self.request.user.TOTP.now()
        self.request.app.notify(TwoFAEvent(self.request, token))
        print(token)
        return {"form": form}

    @trigger("Überprüfen", css="btn btn-primary")
    def validate(self, request, data):
        form = self.setupForm(formdata=data.form)
        if not form.validate():
            return {"form": form}

        twoFA = request.app.utilities.get("twoFA")
        twoFA.validate_twoFA(self.request.environ)
        return horseman.response.redirect("/")

    @trigger("Neuen Key anfordern", css="btn btn-primary")
    def request_token(self, request, data):
        token = request.user.TOTP.now()
        self.request.app.notify(TwoFAEvent(self.request, token))
        print(token)
        form = self.setupForm()
        return {"form": form}


@ui.register_slot(request=Request, name="below-content", view=TwoFA)
def QRCode(request, name, view):
    URI = request.user.OTP_URI
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(URI)
    qr.make(fit=True)
    img = qr.make_image(fill="black", back_color="white")
    buffer = BytesIO()
    img.save(buffer, format="PNG")
    img_str = base64.b64encode(buffer.getvalue()).decode("utf-8")
    return f"""<img src="data:image/png;base64,{img_str}" />"""
