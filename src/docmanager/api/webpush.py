import json
import horseman.meta
import horseman.response
import pywebpush
from datetime import datetime, timedelta
from docmanager.app import api


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
        token = data.json['subscription']
        return horseman.response.Response.create(200)


@api.route("/webpush", methods=['POST'])
def push(request):
    webpush = request.app.plugins["webpush"]
    data = request.extract()
    token = data.json['sub_token']
    message = data.json['message']

    if token is None:
        return horseman.response.Response.to_json(
            400, body={'failed': 1}
        )

    try:
        info = json.loads(token)
        ts = datetime.timestamp(datetime.now() + timedelta(hours=1))
        claims = {**webpush.claims, 'exp': ts}
        pywebpush.webpush(
            subscription_info=info,
            data=message,
            vapid_private_key=webpush.private_key,
            vapid_claims=claims
        )
        return horseman.response.Response.to_json(
            200, body={'success': 1}
        )
    except pywebpush.WebPushException as e:
        print("error",e)
        return horseman.response.Response.to_json(
            400, body={'failed': str(e)}
        )
