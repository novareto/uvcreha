import wrapt
import reg
import horseman.response
from pathlib import Path

from .utils import TemplateLoader
from .resources import siguvtheme
from docmanager.request import Request
from horseman.meta import Overhead


TEMPLATES = TemplateLoader(str((Path(__file__).parent / "templates").resolve()), ".pt")


def template(template, layout=None, raw=True):
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


class Layout:
    def __init__(self, name, **namespace):
        self._template = TEMPLATES[name]
        self._namespace = namespace

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

    @reg.dispatch_method(reg.match_instance('request'), reg.match_key("name"))
    def slot(self, request, name):
        raise RuntimeError("Unknown slot.")

    def register_slot(self, request, name):
        def add_slot(slot):
            return self.slot.register(reg.methodify(slot), request=request, name=name)

        return add_slot


layout = Layout("layout.pt")


@layout.register_slot(request=Request, name="sitecap")
@template(template=TEMPLATES["sitecap.pt"])
def sitecap(request, name):
    return dict(request=request)


@layout.register_slot(request=Request, name="globalmenu")
@template(TEMPLATES["globalmenu.pt"], layout=None, raw=True)
def globalmenu(request, name):
    return dict(request=request)


@layout.register_slot(request=Request, name="navbar")
@template(TEMPLATES["navbar.pt"], layout=None, raw=True)
def navbar(request, name):
    return dict(request=request)


@layout.register_slot(request=Request, name="sidebar")
@template(TEMPLATES["sidebar.pt"], layout=None, raw=True)
def sidebar(request, name):
    return dict(request=request)
