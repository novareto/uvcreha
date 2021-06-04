from uvcreha.app import browser
from uvcreha.browser.crud import DefaultView, EditForm


@browser.register("/users/{loginname}")
class UserFormIndex(DefaultView):
    title = "User"

    def get_fields(self):
        return self.fields(include=("uid", "loginname", "password", "email"))


@browser.register("/users/{loginname}/edit")
class EditUserForm(EditForm):
    title = "Benutzer anlegen"
    readonly = ("uid",)

    def get_fields(self):
        return self.fields(include=("uid", "loginname", "password", "email"))
