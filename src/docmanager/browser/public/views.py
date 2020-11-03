from docmanager.app import application
from docmanager.request import Request
from docmanager.browser.layout import template, TEMPLATES


@application.routes.register("/")
@template(TEMPLATES['index.pt'], layout_name='default', raw=False)
def index(request: Request):
    return dict(request=request)
