import horseman.response
from docmanager.app import application
from docmanager.request import Request
from docmanager.browser.layout import template, TEMPLATES
from docmanager.browser.openapi import generate_doc


@application.routes.register('/doc')
@template(template=TEMPLATES['swagger.pt'], raw=False)
def doc_swagger(request: Request):
    return {'url': '/openapi.json'}


@application.routes.register('/openapi.json')
def openapi(request: Request):
    open_api = generate_doc(request.app.routes)
    return horseman.response.reply(
        200,
        body=open_api.json(by_alias=True, exclude_none=True, indent=2),
        headers={'Content-Type': 'application/json'}
    )
