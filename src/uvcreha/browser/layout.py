import pathlib
from reiter.application.browser import TemplateLoader
from uvcreha.request import Request
from uvcreha.browser.resources import siguvtheme
from uvcreha.app import browser


TEMPLATES = TemplateLoader('./templates')


@browser.ui.register_layout(Request)
class Layout:

    __slots__ = ('_template', 'name')

    def __init__(self, request, name):
        self.name = name
        self._template = TEMPLATES["layout.pt"]

    @property
    def macros(self):
        return self._template.macros

    def render(self, content, **namespace):
        siguvtheme.need()
        return self._template.render(content=content, **namespace)


@browser.ui.register_slot(request=Request, name="sitecap")
def sitecap(request, name):
    return TEMPLATES["sitecap.pt"].render(request=request)


@browser.ui.register_slot(request=Request, name="globalmenu")
def globalmenu(request, name):
    return TEMPLATES["globalmenu.pt"].render(request=request)


@browser.ui.register_slot(request=Request, name="navbar")
def navbar(request, name):
    return TEMPLATES["navbar.pt"].render(request=request)


@browser.ui.register_slot(request=Request, name="sidebar")
def sidebar(request, name):
    return TEMPLATES["sidebar.pt"].render(request=request)


@browser.ui.register_slot(request=Request, name="footer")
def footer(request, name):
    return TEMPLATES["footer.pt"].render(request=request)
