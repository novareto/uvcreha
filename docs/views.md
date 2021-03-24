# Views


## Beispiel für einen View




```python

from fanstatic import Resource, Library
from reiter.view.meta import View
from uvcreha.app import browser
from bg.example import TEMPLATES

from pydantic import BaseModel
from uvcreha.browser.form import FormView
from reiter.form import trigger


@browser.route("/test")
class TestView(View):

    template = TEMPLATES["test_views.pt"]

    def GET(self):
        return dict(request=self.request)
```

