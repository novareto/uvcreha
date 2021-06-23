import reiter.view.composed
from uvcreha.browser.views import layout_rendering
from uvcreha.browser.layout import TEMPLATES


class ComposedView(reiter.view.composed.ComposedView):
    template = TEMPLATES["composed.pt"]
    navs = TEMPLATES["composed_navs.pt"]
    render = layout_rendering

    def get_page(self):
        return self.request.query.get("page", default="default")

    def __call__(self):
        self.update()
        raw = self.request.query.bool("raw", default=False)
        body = self.page(raw=True, layout=None)
        if raw:
            return Response.create(200, body=body)
        pages = [(key, view.title) for key, view in self.pages.items()]
        return self.render(
            {
                "innerpage": body,
                "view": self,
                "local_macros": self.navs.macros,
                "pages": pages,
                "basepage": self.request.route.path,
            }
        )
