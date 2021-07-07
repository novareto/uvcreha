# Views


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

