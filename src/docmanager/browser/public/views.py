from horseman.response import Response
from docmanager.app import application
from docmanager.request import Request
from docmanager.browser.layout import template, TEMPLATES


@application.routes.register("/user")
@template(TEMPLATES["index.pt"], layout_name="default", raw=False,)
def user(request: Request):
    request.flash().add(body="BLA BLUB")
    request.app.plugins['amqp'].send('Some message', key='object.add')
    return dict(request=request, user=None)


@application.routes.register("/")
@template(TEMPLATES["index.pt"], layout_name="default", raw=False,)
def index(request: Request):
    request.app.plugins['amqp'].send('Some message', key='object.add')
    return Response.create(200, body=b'Message sent')
