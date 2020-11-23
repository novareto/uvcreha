import horseman.response
import horseman.meta
from docmanager.app import browser
from docmanager.browser.layout import template, TEMPLATES
from docmanager.browser.openapi import generate_doc
from docmanager.db import User
from docmanager.request import Request


@browser.routes.register("/doc")
@template(TEMPLATES["swagger.pt"], raw=False)
def doc_swagger(request: Request):
    return {"url": "/openapi.json"}


@browser.routes.register("/openapi.json")
def openapi(request: Request):
    open_api = generate_doc(request.app.routes)
    return horseman.response.reply(
        200,
        body=open_api.json(by_alias=True, exclude_none=True, indent=2),
        headers={"Content-Type": "application/json"}
    )


@browser.route("/")
@template(TEMPLATES["index.pt"], layout_name="default", raw=False)
def index(request: Request):
    user = User(request.db_session)
    return dict(request=request, user=user)


@browser.route("/webpush")
@template(TEMPLATES["webpush.pt"], layout_name="default", raw=False)
def webpush(request: Request):
    return dict(request=request)


@browser.route("/subscription", name="webpush_subscription")
class Webpush(horseman.meta.APIView):

    def GET(self, request: Request):
        """get vapid public key
        """
        webpush = request.app.plugins.get("webpush")
        return horseman.reponse.Response.to_json(
            200,
            body={
                "public_key": webpush.vapid_public_key
            },
            headers={
                "Access-Control-Allow-Origin": "*"
            }
        )

    def POST(self, request: Request):
        """store subscription information
        """
        data = request.extract()
        token = data['form'].get('subscription_token')
        if token is not None:
            return horseman.reponse.Response.create(201)
        return horseman.reponse.Response.create(400)
