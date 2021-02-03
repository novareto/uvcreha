import pathlib
import horseman.response
from reiter.application.browser import TemplateLoader, registries
from docmanager.request import Request
from docmanager.browser.resources import siguvtheme


TEMPLATES = TemplateLoader(
    str((pathlib.Path(__file__).parent / "templates").resolve()), ".pt")


UI = registries.UIRegistry()


@UI.register_layout(Request)
class Layout:

    __slots__ = ('_template',)

    def __init__(self, request, name):
        self._template = TEMPLATES["layout.pt"]

    @property
    def user(self):
        return None

    @property
    def macros(self):
        return self._template.macros

    def render(self, content, **namespace):
        siguvtheme.need()
        return self._template.render(content=content, **namespace)


@UI.register_slot(request=Request, name="sitecap")
def sitecap(request, name):
    return TEMPLATES["sitecap.pt"].render(request=request)


@UI.register_slot(request=Request, name="globalmenu")
def globalmenu(request, name):
    return TEMPLATES["globalmenu.pt"].render(request=request)


@UI.register_slot(request=Request, name="navbar")
def navbar(request, name):
    return TEMPLATES["navbar.pt"].render(request=request)


@UI.register_slot(request=Request, name="sidebar")
def sidebar(request, name):
    return TEMPLATES["sidebar.pt"].render(request=request)


@UI.register_slot(request=Request, name="footer")
def footer(request, name):
    return TEMPLATES["footer.pt"].render(request=request)
