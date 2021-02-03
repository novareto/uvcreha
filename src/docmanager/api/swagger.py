
import horseman.response
import horseman.meta
from docmanager.app import api
from docmanager.browser.layout import UI, TEMPLATES
from docmanager.request import Request
from docmanager.browser.openapi import generate_doc


@api.route("/doc")
def doc_swagger(request: Request):
    return horseman.response.reply(
        UI.render(TEMPLATES["swagger.pt"], url="/openapi.json"))


@api.route("/openapi.json")
def openapi(request: Request):
    open_api = generate_doc(request.app.routes)
    return horseman.response.reply(
        200,
        body=open_api.json(by_alias=True, exclude_none=True, indent=2),
        headers={"Content-Type": "application/json"}
    )
