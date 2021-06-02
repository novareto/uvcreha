from horseman.http import HTTPError
from horseman.response import Response
from reiter.application.registries import NamedComponents
from reiter.view.meta import View
from uvcreha.browser.layout import TEMPLATES


class ComposedViewMeta(type):

    def __init__(cls, name, bases, attrs):
        type.__init__(cls, name, bases, attrs)
        cls.pages = NamedComponents()


class ComposedView(View, metaclass=ComposedViewMeta):
    template = TEMPLATES["composed.pt"]
    navs = TEMPLATES["composed_navs.pt"]

    def GET(self):
        # allowed method
        pass

    def POST(self):
        # allowed method
        pass

    def update(self):
        name = self.request.query.get('page', default="default")
        page = self.pages.get(name)
        if page is None:
            raise HTTPError(400)
        self.page = page(self.request, **self.params)
        self.page.update()

    def __call__(self):
        self.update()
        raw = self.request.query.bool('raw', default=False)
        body = self.page(raw=True, layout=None)
        if raw:
            return Response.create(200, body=body)
        pages = [(key, view.title) for key, view in self.pages.items()]
        return self.render({
            'innerpage': body,
            'view': self, 'local_macros': self.navs.macros,
            'pages': pages, 'basepage': self.request.route.path
        })


# @browser.ui.register_slot(
#     request=Request, view=ComposedView, name="above-content")
# def composedpages(request, name, view):
#     pages = [(key, view.title) for key, view in view.pages.items()]
#     return TEMPLATES["composed_navs.pt"].render(
#         request=request, pages=pages, basepage=request.route.path
#     )
