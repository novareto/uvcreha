import datetime
import json
import horseman.meta
import horseman.response
import pywebpush

from docmanager.app import api
from docmanager.db import WebpushSubscription


@api.route("/subscription", name="webpush_subscription")
class Webpush(horseman.meta.APIView):

    def GET(self, request):
        """get vapid public key
        """
        webpush = request.app.plugins.get("webpush")
        return horseman.response.Response.to_json(
            200,
            body={
                "public_key": webpush.public_key
            },
            headers={
                "Access-Control-Allow-Origin": "*"
            }
        )

    def POST(self, request):
        """store subscription information
        """
        data = request.extract()
        token = data['form'].get('subscription_token')
        if token is not None:
            return horseman.response.Response.create(201)
        return horseman.response.Response.create(400)


@api.route("/webpush", methods=['POST'])
def push_v1(request):

    webpush = request.app.plugins["webpush"]
    message = "Push Test v1"
    data = request.extract()

    token = data['form'].get('sub_token')

    if token is None:
        return horseman.response.Response.to_json(
            400, body={'failed': 1}
        )

    try:
        info = json.loads(token)
        pywebpush.webpush(
            subscription_info=info,
            data=message,
            vapid_private_key=webpush.vapid_private_key,
            vapid_claims=webpush.vapid_claims
        )
        return horseman.response.Response.to_json(
            200, body={'success': 1}
        )
    except pywebpush.WebPushException as e:
        print("error",e)
        return horseman.response.Response.to_json(
            400, body={'failed': str(e)}
        )
