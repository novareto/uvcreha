from horseman.response import Response
from uvcreha.api import routes
from uvcreha.app import browser
from uvcreha.browser.layout import TEMPLATES


@browser.register('/openapi')
def openapi(request):
    return Response.to_json(body=routes.spec.to_dict())


@browser.register('/swagger')
def swagger(request):
    html = TEMPLATES['swagger'].render()
    return Response.html(body=html)
