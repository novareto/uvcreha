from uvcreha import models
from uvcreha.app import browser
from uvcreha.browser.crud import DefaultView, EditForm


@browser.route("/users/{uid}/files/{az}")
class FileIndex(DefaultView):
    model = models.File


@browser.route("/users/{uid}/files/{az}/edit")
class FileEdit(EditForm):
    model = models.File
    readonly = ('uid', 'az')
