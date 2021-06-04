from reiter.application.browser import TemplateLoader
from uvcreha.request import Request
from uvcreha.browser.resources import siguvtheme
from uvcreha.app import ui


TEMPLATES = TemplateLoader('./templates')


@ui.register_layout(Request)
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


@ui.register_slot(request=Request, name="sitecap")
def sitecap(request, name, view):
    return TEMPLATES["sitecap.pt"].render(request=request)


@ui.register_slot(request=Request, name="globalmenu")
def globalmenu(request, name, view):
    return TEMPLATES["globalmenu.pt"].render(request=request)


@ui.register_slot(request=Request, name="navbar")
def navbar(request, name, view):
    return TEMPLATES["navbar.pt"].render(request=request)


@ui.register_slot(request=Request, name="sidebar")
def sidebar(request, name, view):
    return TEMPLATES["sidebar.pt"].render(request=request)


@ui.register_slot(request=Request, name="site-messages")
def messages(request, name, view):
    utility = request.utilities.get('flash')
    if utility is not None:
        messages = list(utility)
    else:
        messages = []
    return TEMPLATES["messages.pt"].render(messages=messages)


@ui.register_slot(request=Request, name="footer")
def footer(request, name, view):
    return TEMPLATES["footer.pt"].render(request=request)
