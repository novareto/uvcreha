from reiter.view.meta import View, APIView
from uvcreha.app import browser
from uvcreha.browser.layout import TEMPLATES
from uvcreha import contenttypes


def layout_rendering(view: View, result: Result, raw=False, layout=...):
    if isinstance(result, str):
        if raw:
            return result
        return Response.create(body=result)

    if isinstance(result, (dict, type(None))):
        if view.template is None:
            raise ValueError(
                "{view} returned a namespace but does "
                "not define a template")
        if result is None:
            ns = view.namespace()
        else:
            ns = view.namespace(**result)
        if raw:
            return view.request.app.ui.render(
                view.template, layout=layout, **ns)
        return view.request.app.ui.response(
            view.template, layout=layout, **ns)

    if isinstance(result, Response):
        if raw:
            raise ValueError('The view returned a Response object.')
        return result

    raise ValueError("Can't interpret return")


class View(APIView):
    render = layout_rendering


@browser.register("/")
class LandingPage(View):

    template = TEMPLATES["index.pt"]

    def GET(self):
        user = self.request.user
        # flash_messages = self.request.utilities.get("flash")
        # flash_messages.add(body="HELLO WORLD.")
        #self.request.app.utilities['amqp'].send(
        #    {'test': 'YEAH'}, key='object.add'
        #)
        return {"user": user}

    def get_files(self, key):
        ct = contenttypes.registry["file"]
        files = ct.bind(self.request.database).find(uid=key)
        return files

    def get_documents(self, uid, az):
        ct = contenttypes.registry["document"]
        docs = ct.bind(self.request.database).find(uid=uid, az=az)
        return docs


@browser.register("/webpush")
class Webpush(View):
    template = TEMPLATES["webpush.pt"]

    def GET(self):
        return dict(request=self.request)

    def POST(self):
        wp = self.request.app.utilities["webpush"]
        wp.send(
            message="klaus",
            token=self.request.user.preferences.webpush_subscription
        )
        return dict(success="ok")
