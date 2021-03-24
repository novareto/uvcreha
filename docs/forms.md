# Forms 


## Beispiel für eine Form






```python
from fanstatic import Resource, Library
from reiter.view.meta import View
from uvcreha.app import browser
from bg.example import TEMPLATES

from pydantic import BaseModel
from uvcreha.browser.form import FormView
from reiter.form import trigger


class Person(BaseModel):

    name: str
    age: int


@browser.route("/test_form")
class TestForm(FormView):
    title = "Titel"
    description = "Description"
    model = Person

    @trigger(title="Speichern", id="save")
    def handel_save(self, request, data):
        form = self.setupForm(formdata=data.form)
        if not form.validate():
            return {"form": form}
        return {"form": form}

```

