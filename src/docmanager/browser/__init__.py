import logging
import chameleon.zpt.loader
from pkg_resources import iter_entry_points
from reiter.application.response import Response
from docmanager.browser.layout import UI


DEFAULT_LAYOUT = 'default'


def render_template(
        template: str, namespace: dict, layout: DEFAULT_LAYOUT,
        code: HTTPCode = 200, headers: Optional[dict] = None):

    if layout is not None:
        layout = UI.layout(request, layout)
        content = template.render(macros=layout.macros, **namespace)
                path = request.environ["PATH_INFO"]
                baseurl = "{}://{}{}/".format(
                    request.environ["wsgi.url_scheme"],
                    request.environ["HTTP_HOST"],
                    request.environ["SCRIPT_NAME"],
                )
                body = layout.render(
                    content,
                    path=path,
                    baseurl=baseurl,
                    request=request,
                    context=object(),
                    user=None,
                    messages=flash_messages,
                    view=instance,
                )
