# Views / Layout / Viewlets

## Beispiel für einen View


```python


from uvcreha.browser.views import View
from uvcreha.app import browser
from bg.example import TEMPLATES


@browser.register("/test")
class TestView(View):

    template = TEMPLATES["test_views.pt"]

    def GET(self):
        return dict(request=self.request)

```

Ein komplettes Layout kann man wiefolgt registriert.


```python

@ui.register_layout(Request, name="bg.example")
class BGExampleLayout:

    __slots__ = ("_template", "name")

    def __init__(self, request, name):
        self.name = name
        self._template = TEMPLATES["layout.pt"]

    @property
    def macros(self):
        return self._template.macros

    def render(self, content, **namespace):
        return self._template.render(content=content, **namespace)


```

Viewlets können werden wiefolgt registriert.


```python

@ui.register_slot(request=Request, name="sitecap")
def sitecap(request, name, view):
    return TEMPLATES["sitecap.pt"].render(request=request)

```
