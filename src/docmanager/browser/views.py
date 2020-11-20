import horseman.response

from docmanager.app import browser
from docmanager.browser.layout import template, TEMPLATES
from docmanager.browser.openapi import generate_doc
from docmanager.db import User
from docmanager.request import Request


@browser.routes.register('/doc')
@template(TEMPLATES['swagger.pt'], raw=False)
def doc_swagger(request: Request):
    return {'url': '/openapi.json'}


@browser.routes.register('/openapi.json')
def openapi(request: Request):
    open_api = generate_doc(request.app.routes)
    return horseman.response.reply(
        200,
        body=open_api.json(by_alias=True, exclude_none=True, indent=2),
        headers={'Content-Type': 'application/json'}
    )


@browser.route("/")
@template(TEMPLATES["index.pt"], layout_name="default", raw=False)
def index(request: Request):
    user = User(request.db_session)
    return dict(request=request, user=user)
