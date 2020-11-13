from docmanager.app import application
from docmanager.request import Request
from docmanager.browser.layout import template, TEMPLATES
from docmanager.db import User, File


@application.routes.register("/", permissions={"document.view"},)
@template(TEMPLATES["index.pt"], layout_name="default", raw=False,)
def index(request: Request):
    request.flash().add(body="BLA BLUB")
    user = User(request.app.database.session)
    return dict(request=request, user=user)
