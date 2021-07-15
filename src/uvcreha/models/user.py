import pyotp
import base64
import hashlib
from uvcreha import events
from uvcreha.workflow import user_workflow
from uvcreha.jsonschema import store
from uvcreha.contenttypes import registry, Content


store.add(
    "UserPreferences",
    {
        "id": "UserPreferences",
        "title": "User preferences",
        "description": "User-based application preferences",
        "type": "object",
        "properties": {
            "name": {"title": "Vorname", "description": "Vorname", "type": "string"},
            "surname": {
                "title": "Nachname",
                "description": "Nachname",
                "type": "string",
            },
            "birthdate": {"title": "Geburtsdatum", "type": "string", "format": "date"},
            "datenschutz": {
                "title": "Datenschutz",
                "description": (
                    "Bitte best\u00e4tigen Sie hier, dass Sie "
                    "die Ausf\u00fchrungen zum Datenschutzgelesen und "
                    "akzeptiert haben."
                ),
                "default": False,
                "type": "boolean",
            },
            "teilnahme": {
                "title": "Teilnahme",
                "description": (
                    "Bitte best\u00e4tigen Sie uns hier die Teilnahme "
                    "am Online-Verfahren."
                ),
                "default": False,
                "type": "boolean",
            },
            "mobile": {
                "title": "Telefonnummer",
                "description": "Telefonnummer",
                "type": "string",
            },
            "messaging_type": {
                "title": "Benachrichtigungen",
                "description": (
                    "Bitte w\u00e4hlen Sie eine/oder mehrere Arten der "
                    "Benachrichtiung aus"
                ),
                "default": ["email"],
                "type": "array",
                "items": {"$ref": "#/definitions/MessagingType"},
            },
            "webpush_subscription": {
                "title": "Webpush Subscription",
                "default": "",
                "type": "string",
            },
            "webpush_activated": {
                "title": "Webpush Activated",
                "default": False,
                "type": "boolean",
            },
        },
        "definitions": {
            "MessagingType": {
                "title": "MessagingType",
                "description": "Messaging system choices.",
                "enum": ["email", "webpush"],
                "type": "string",
            }
        },
    },
)


store.add(
    "User",
    {
        "id": "User",
        "title": "User model",
        "type": "object",
        "properties": {
            "uid": {"title": "ID", "description": "Internal User ID", "type": "string"},
            "loginname": {
                "title": "Loginname",
                "description": "Bitte tragen Sie hier den Loginnamen ein.",
                "type": "string",
            },
            "password": {
                "title": "Passwort",
                "description": "Bitte tragen Sie hier das Kennwort ein.",
                "type": "string",
                "writeOnly": True,
                "format": "password",
            },
            "email": {
                "title": "E-Mail",
                "description": "Bitte geben Sie die E-Mail ein",
                "type": "string",
                "format": "email",
            },
            "creation_date": {
                "title": "Creation Date",
                "type": "string",
                "format": "date-time",
            },
            "state": {"title": "State", "default": "pending", "type": "string"},
            "permissions": {
                "title": "Permissions",
                "default": ["document.view"],
                "type": "array",
                "items": {},
            },
            "preferences": {"$ref": "UserPreferences/"},
        },
        "required": ["uid", "loginname", "password"],
    },
)


@registry.factory(
    "user", schema=store.get("User"), collection="users")
class User(Content):

    @property
    def id(self):
        return self["uid"]

    @property
    def title(self):
        return self["loginname"]

    @property
    def state(self):
        wf = user_workflow(self)
        return wf.state

    @property
    def shared_key(self) -> bytes:
        key = hashlib.sha256(self["uid"].encode("utf-8"))
        key.update(self["loginname"].encode("utf-8"))
        return base64.b32encode(key.digest())

    @property
    def TOTP(self) -> bytes:
        """We use mostly default values for Google Authenticator compat.
        """
        return pyotp.TOTP(
            self.shared_key,
            name=self["loginname"],
        )

    @property
    def OTP_URI(self) -> str:
        return self.TOTP.provisioning_uri()

    def generate_token(
            self, digits=8, digest=hashlib.sha256, interval=60*60):  # 1h
        return pyotp.TOTP(
            self.shared_key,
            name=self["loginname"],
            digits=digits,
            digest=digest,
            interval=interval
        )


@User.actions.register("default", title="View")
def view(request, item):
    return request.route_path("user.view", uid=item["uid"])


@User.actions.register("edit", title="Bearbeiten", css="fa fa-edit")
def edit(request, item):
    return request.route_path("user.edit", uid=item["uid"])


@User.actions.register("edit", title="Akte anlegen", css="fa fa-folder")
def new_file(request, item):
    return request.route_path("user.new_file", uid=item["uid"])
