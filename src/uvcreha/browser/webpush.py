import json
import horseman.meta
import horseman.response
from reiter.view.meta import View
from uvcreha.app import browser


@browser.register("/webpush/subscription", name="webpush_subscription")
class Webpush(View):
    def GET(self):
        """get vapid public key"""
        webpush = self.request.app.utilities["webpush"]
        return horseman.response.Response.to_json(
            200,
            body={"public_key": webpush.public_key},
            headers={"Access-Control-Allow-Origin": "*"},
        )

    def POST(self):
        """store subscription information"""
        data = self.request.extract()
        token = data.json["subscription"]
        self.request.user.preferences.webpush_subscription = json.dumps(token)
        # user = self.request.database(User)
        # user.update(
        #     self.request.user.key,
        #     preferences=self.request.user.preferences.dict()
        # )
        # return horseman.response.Response.create(200)
