import datetime
import json
from docmanager.app import api
from docmanager.db import WebpushSubscription
from horseman.response import Response
import pywebpush


@api.route("/push_v1/", methods=['POST'])
def push_v1(request):

    webpush = request.app.plugins["webpush"]
    message = "Push Test v1"
    data = request.extract()
    token = data['form'].get('sub_token')

    if token is None:
        return Response.to_json(400, body={'failed': 1})

    try:

        info = json.loads(token)
        pywebpush.webpush(
            subscription_info=info,
            data=message,
            vapid_private_key=webpush.vapid_private_key,
            vapid_claims=webpush.vapid_claims
        )
        return Response.to_json(200, body={'success': 1})
    except pywebpush.WebPushException as e:
        print("error",e)
        return Response.to_json(400, body={'failed': str(e)})
