from typing import ClassVar
from horseman.http import HTTPError
from horseman.response import Response
from reiter.application.registries import NamedComponents
from reiter.view.meta import View
from uvcreha.app import browser
from uvcreha.browser.layout import TEMPLATES
from uvcreha.request import Request


class ComposedViewMeta(type):

    def __init__(cls, name, bases, attrs):
        type.__init__(cls, name, bases, attrs)
        cls.pages = NamedComponents()


class ComposedView(View, metaclass=ComposedViewMeta):

    def update(self):
        name = self.request.query.get('page', default="default")
        page = self.pages.get(name)
        if page is None:
            raise HTTPError(400)
        self.page = page(self.request, **self.params)
        self.page.update()

    def __call__(self):
        raw = self.request.query.bool('raw', default=False)
        if raw:
            self.update()
            if worker := getattr(self.page, self.method, None):
                return self.render(worker())
            raise HTTPError(405)
        return super().__call__()


@browser.ui.register_slot(
    request=Request, view=ComposedView, name="above-content")
def composedpages(request, name, view):
    pages = [(key, view.title) for key, view in view.pages.items()]
    return TEMPLATES["pages.pt"].render(
        request=request, pages=pages, basepage=request.route.path
    )
