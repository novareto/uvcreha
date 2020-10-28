import pathlib
import reg
import wrapt
import horseman.response

from horseman.meta import Overhead
from docmanager.utils import TemplateLoader
from docmanager.resources import siguvtheme
from docmanager.request import Request
from docmanager.app import application


TEMPLATES = TemplateLoader(
    str((pathlib.Path(__file__).parent / "templates").resolve()), ".pt")


def template(template, layout_name=None, raw=False):
    @wrapt.decorator
    def render(endpoint, instance, args, kwargs):
        result = endpoint(*args, **kwargs)
        if isinstance(result, horseman.response.Response):
            return result
        assert isinstance(result, dict)

        if args:
            request = args[0]
        else:
            request = kwargs["request"]

        if layout_name is not None:
            layout = request.app.layout(request, layout_name)
        else:
            layout = None

        if layout is not None:
            path = request.environ["PATH_INFO"]
            baseurl = "{}://{}{}/".format(
                request.environ["wsgi.url_scheme"],
                request.environ["HTTP_HOST"],
                request.environ["SCRIPT_NAME"],
            )

            if (fm := getattr(request, "flash", None)) is not None:
                messages = fm.hasMessages and fm.exhaustMessages() or None
            else:
                messages = None

            content = template.render(macros=layout.macros, **result)
            body = layout.render(
                content,
                path=path,
                baseurl=baseurl,
                request=request,
                context=object(),
                user=None,
                messages=messages,
                view=instance,
            )
            if raw:
                return body
            return horseman.response.reply(
                body=body, headers={"Content-Type": "text/html; charset=utf-8"}
            )

        content = template.render(**result)
        if raw:
            return content
        return horseman.response.reply(
            body=content, headers={"Content-Type": "text/html; charset=utf-8"}
        )

    return render


@application.ui.register_layout(Request)
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


@application.ui.register_slot(request=Request, name="sitecap")
@template(template=TEMPLATES["sitecap.pt"])
def sitecap(request, name):
    return dict(request=request)


@application.ui.register_slot(request=Request, name="globalmenu")
@template(TEMPLATES["globalmenu.pt"], raw=True)
def globalmenu(request, name):
    return dict(request=request)


@application.ui.register_slot(request=Request, name="navbar")
@template(TEMPLATES["navbar.pt"], raw=True)
def navbar(request, name):
    return dict(request=request)


@application.ui.register_slot(request=Request, name="sidebar")
@template(TEMPLATES["sidebar.pt"], raw=True)
def sidebar(request, name):
    return dict(request=request)

@layout.register_slot(request=Request, name="footer")
@template(TEMPLATES["footer.pt"], layout=None, raw=True)
def sidebar(request, name):
    return dict(request=request)
