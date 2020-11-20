import datetime
from docmanager.app import api
from docmanager.db import WebpushSubscription
from horseman.response import Response
from pywebpush import webpush, WebPushException


WEBPUSH_VAPID_PRIVATE_KEY = """
MIGHAgEAMBMGByqGSM49AgEGCCqGSM49AwEHBG0wawIBAQQgwihUmiIrnarGSRK4
iNxWjBUK+9tO2+NdV2TlMTuE+2uhRANCAATd2CyJvdTA3nzQN46FZySjs7SEyg72
8cdzlaLdd3+RJKWlvS4TZE/77nr1rbfmAGzXPxDFdkbCzpnUrnFITIFV
"""


@api.route('/webpush/subscribe')
def subscribe(request):
    data = request.extract()
    subscription_info = data['form'].get('subscription_info')
    is_active = bool(data['form'].get('is_active'))

    model = WebpushSubscription(request.db_session)
    item = model.find_one({
        'subscription_info': subscription_info
    })
    if item is None:
        item = model.create(
            is_active=is_active,
            subscription_info=subscription_info
        )
    return Response.to_json(200, body={'id': item.id})


@api.route('/webpush/notify')
def notify(request):
    model = WebpushSubscription(request.db_session)
    items = model.find({
        'is_active': True
    })

    for item in items:
        try:
            webpush(
                subscription_info=item.subscription_info_json,
                data="Test 123",
                vapid_private_key=WEBPUSH_VAPID_PRIVATE_KEY,
                vapid_claims={
                    "sub": "mailto:webpush@mydomain.com"
                }
            )
        except WebPushException as ex:
            logging.exception("webpush fail")

    return "{} notification(s) sent".format(count)
