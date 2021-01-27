import pathlib
import horseman.response
from reiter.application.browser import TemplateLoader
from docmanager.request import Request
from docmanager.browser.resources import siguvtheme


TEMPLATES = TemplateLoader(
    str((pathlib.Path(__file__).parent / "templates").resolve()), ".pt")


UI = registries.UIRegistry()


@UI.register_layout(Request)
class Layout:

    def __init__(self, request, name):
        self._template = TEMPLATES["layout.pt"]
        self._namespace = {'request': request}

    @property
    def user(self):
        return None

    @property
    def macros(self):
        return self._template.macros

    def render(self, content, **extra):
        siguvtheme.need()
        ns = {**self._namespace, **extra}
        return self._template.render(content=content, **ns)


@UI.register_slot(request=Request, name="sitecap")
@template(TEMPLATES["sitecap.pt"], raw=True)
def sitecap(request, name):
    return dict(request=request)


@UI.register_slot(request=Request, name="globalmenu")
@template(TEMPLATES["globalmenu.pt"], raw=True)
def globalmenu(request, name):
    return dict(request=request)


@UI.register_slot(request=Request, name="navbar")
@template(TEMPLATES["navbar.pt"], raw=True)
def navbar(request, name):
    return dict(request=request)


@UI.register_slot(request=Request, name="sidebar")
@template(TEMPLATES["sidebar.pt"], raw=True)
def sidebar(request, name):
    return dict(request=request)


@UI.register_slot(request=Request, name="footer")
@template(TEMPLATES["footer.pt"], raw=True)
def footer(request, name):
    return dict(request=request)
