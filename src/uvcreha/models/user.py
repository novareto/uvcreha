import enum
import pyotp
import base64
import hashlib
from uvcreha.workflow import user_workflow
from uvcreha.jsonschema import store
from uvcreha.contenttypes import registry, Content


@registry.factory("user", schema=store.get('User'), collection="users")
class User(Content):

    @property
    def id(self):
        return self['uid']

    @property
    def title(self):
        return self['loginname']

    @property
    def state(self):
        wf = user_workflow(self)
        return wf.state

    @property
    def shared_key(self) -> bytes:
        key = hashlib.sha256(self['uid'].encode('utf-8'))
        key.update(self['loginname'].encode('utf-8'))
        return base64.b32encode(key.digest())

    @property
    def TOTP(self) -> bytes:
        return pyotp.TOTP(
            self.shared_key,
            digits=8,
            digest=hashlib.sha256,
            name=self['loginname'],
            interval=60
        )

    @property
    def OTP_URI(self) -> str:
        return self.TOTP.provisioning_uri()


@User.actions.register('default', title="View")
def view(request, item):
    return request.route_path('user.view', uid=item['uid'])


@User.actions.register('edit', title="Bearbeiten", css='fa fa-edit')
def edit(request, item):
    return request.route_path('user.edit', uid=item['uid'])


@User.actions.register('edit', title="Akte anlegen", css='fa fa-folder')
def new_file(request, item):
    return request.route_path('user.new_file', uid=item['uid'])
