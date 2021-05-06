from uvcreha.app import browser
from uvcreha.browser.crud import DefaultView, EditForm
from uvcreha.models import User


@browser.route("/users/{loginname}")
class UserFormIndex(DefaultView):
    title = "User"
    model = User

    def get_fields(self):
        return self.fields(
            include=("uid", "loginname", "password", "email")
        )


@browser.route("/users/{loginname}/edit")
class EditUserForm(EditForm):
    title = "Benutzer anlegen"
    model = User
    readonly = ('uid',)

    def get_fields(self):
        return self.fields(
            include=("uid", "loginname", "password", "email")
        )
