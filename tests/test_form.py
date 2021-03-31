from uvcreha.browser.form import FormView
from reiter.form import trigger
from pydantic import BaseModel
from uvcreha.request import Request


def _test_form():

    class Route:
        path = "myform"

    class MyModel(BaseModel):

        name: str
        age: int

    class MyForm(FormView):
        title = "myForm"
        model = MyModel

        @trigger(title='Speichern', id="kk")
        def handle_save(self):
            data = self.reqeust.form
            print(data)

    request = Request('app', {'REQUEST_METHOD': 'GET'}, Route())
    myform = MyForm(request)
    assert myform.title == "myForm"
    assert myform.model is MyModel
