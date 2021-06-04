from horseman.http import Multidict
from uvcreha.app import browser
from reiter.form import trigger
from uvcreha.browser.form import Form, FormView
from uvcreha import jsonschema, contenttypes


@browser.register("/preferences")
class EditPreferences(FormView):

    title = "E-Mail Adresse ändern"
    description = "Edit your preferences."
    action = "preferences"

    @trigger("abbrechen", "Abbrechen", css="btn btn-secondary")
    def abbrechen(self, request):
        pass

    def setupForm(self, data=None, formdata=Multidict()):
        if data is None:
            data = self.request.user.data.get('preferences', {})
        schema = jsonschema.store.get('UserPreferences')
        form = Form.from_schema(schema)
        form.process(data=data, formdata=formdata)
        return form

    @trigger("update", "Update", css="btn btn-primary")
    def do_update(self, request):
        data = request.extract()["form"]
        form = self.setupForm(formdata=data)
        if not form.validate():
            return {"form": form}
        user = contenttypes.registry['user'].bind(self.request.database)
        user.update(request.user.key, preferences=data.dict())
        return self.redirect("/")
