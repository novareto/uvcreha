from dataclasses import dataclass, field
from typing import Optional

import horseman.meta
import horseman.response
import horseman.http
from reiter.application.app import Application
from reiter.application.browser import registries
from reiter.arango.connector import Connector
from reiter.arango.validation import ValidationError
from docmanager.security import SecurityError
from docmanager.request import Request


@dataclass
class RESTApplication(Application):

    connector: Optional[Connector] = None
    request_factory: horseman.meta.Overhead = Request

    def __call__(self, environ, start_response):
        try:
            if self._caller is not None:
                return self._caller(environ, start_response)
            return super().__call__(environ, start_response)
        except ValidationError as exc:
            return exc(environ, start_response)


@dataclass
class Browser(RESTApplication):

    def check_permissions(self, route, environ):
        if permissions := route.extras.get('permissions'):
            user = environ.get(self.config.env.user)
            if user is None:
                raise SecurityError(None, permissions)
            if not permissions.issubset(user.permissions):
                raise SecurityError(user, permissions - user.permissions)


browser = Browser('Browser Application')
api = RESTApplication('REST Application')
