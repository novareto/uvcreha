from uvcreha.browser.crud import AddForm
from uvcreha import contenttypes
from uvcreha.browser.form import Form, FormView
from uvcreha.workflow import user_workflow
from uvcreha.app import browser, events
from uvcreha.browser.layout import TEMPLATES
from uuid import uuid4
from urllib.parse import urlencode
from horseman.http import Multidict
from jsonschema_wtforms import schema_fields
from uvcreha import contenttypes, jsonschema
from wtforms import StringField
from reiter.form import trigger
from uvcreha.events import UserRegisteredEvent


TEXT = """Vielen Dank für Ihre Registrierung
Bitte klicken Sie auf folgenden Link %s
"""



@browser.register("/self_register", name="self_register")
class AddUserForm(AddForm):
    title = "Benutzer anlegen"
    description = "Benutzer registrieren"

    def update(self):
        self.content_type = contenttypes.registry['user']

    def create(self, data):
        binding = self.content_type.bind(self.request.database)
        data = data.form.dict()
        uid = str(uuid4())
        obj, response = binding.create(**{
            **self.params,
            **data,
            '_key': uid,
            'uid': uid,
            'state': user_workflow.states.pending.name
        })

        token = obj.generate_token().now()
        url = "%s/%s?%s" % (
            self.request.application_uri(),
            self.request.route_path(name='verify_register'),
            urlencode(dict(uid=uid, token=token))
        )
        self.request.app.notify(
            UserRegisteredEvent(request, obj, message=url)
        )
        return obj

    def get_form(self):
        return Form.from_schema(
            self.content_type.schema,
            include=("loginname", "password", "email")
        )


@browser.register("/verify_register", name="verify_register")
class VerifyRegistration(FormView):
    title = "Registrierung abschließen"
    description = ""

    def update(self):
        self.content_type = contenttypes.registry['user']

    def get_fields(self):
        schema = jsonschema.store.get('User')
        return schema_fields(schema, include=("password", "uid"))

    def setupForm(self, data={}, formdata=Multidict()):
        data = self.request.query.dict()
        fields = self.get_fields()
        fields['token'] = StringField('token')
        form = Form(fields)
        form.process(data=data, formdata=formdata)
        return form

    @trigger("speichern", "Registrierung abschließen",
             order=1, css="btn btn-primary")
    def login(self, request, data):
        form = self.setupForm(formdata=data.form)
        flash_messages = request.utilities.get("flash")
        if not form.validate():
            return {"form": form}
        binding = self.content_type.bind(self.request.database)
        data = data.form.dict()
        user = binding.find_one(uid=data['uid'])

        if user is None:
            flash_messages.add(body="Kein Benutzer gefunden.")
            return {"form": form}

        token = user.generate_token()
        if not token.verify(data['token']):
            flash_messages.add(body="Fehler im Token.")
            return {"form": form}

        if data['password'] != user['password']:
            flash_messages.add(body="Fehler Passwort.")
            return {"form": form}

        binding.update(
            uid=data['uid'],
            state=user_workflow.states.active.name
        )
        return self.redirect(request.environ["SCRIPT_NAME"] + "/")
