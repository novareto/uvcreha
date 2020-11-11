from docmanager.app import application
from docmanager.request import Request
from docmanager.browser.layout import template, TEMPLATES
from docmanager.models import Message
from docmanager.db import User, File


@application.routes.register("/", permissions={"document.view"},)
@template(TEMPLATES["index.pt"], layout_name="default", raw=False,)
def index(request: Request):
    request.flash(Message(type="info", body="BLA BLUB"))
    user = User(request.app.database.session)
    return dict(request=request, user=user)


@application.routes.register("/users/{username}/files/{fileid}", permissions={"document.view"},)
@template(TEMPLATES["files.pt"], layout_name="default", raw=False,)
def index_files(request: Request, username: str, fileid: str):
    model = File(request.db_session)
    return dict(request=request, myfile=model)
