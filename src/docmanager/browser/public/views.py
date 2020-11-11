from docmanager.app import application
from docmanager.request import Request
from docmanager.browser.layout import template, TEMPLATES
from docmanager.models import Message


@application.routes.register("/", permissions={"document.view"},)
@template(TEMPLATES["index.pt"], layout_name="default", raw=False,)
def index(request: Request):
    request.flash(Message(type="info", body="BLA BLUB"))
    return dict(request=request)
