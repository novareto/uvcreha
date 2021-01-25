import json
import horseman.meta
import horseman.response
from docmanager.app import browser
from docmanager.models import User


@browser.route("/webpush/subscription", name="webpush_subscription")
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
        request.user.preferences.webpush_subscription = json.dumps(token)
        user = request.database(User)
        user.update(
            request.user.key, preferences=request.user.preferences.dict())
        return horseman.response.Response.create(200)