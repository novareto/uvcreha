import arango
import functools
import fanstatic
import cromlech.session
import cromlech.sessions.file
import horseman.http
import horseman.meta
import horseman.response
import reiter.view.meta

import json
from typing import Optional
from dataclasses import dataclass, field
from fs.osfs import OSFS
from horseman.types import WSGICallable
from reiter.amqp.emitter import AMQPEmitter
from reiter.application.app import Application
from reiter.application.browser import registries
from roughrider.routing.route import NamedRoutes
from roughrider.storage.meta import StorageCenter
from uvcreha.auth import Auth
from uvcreha.database import Connector
from uvcreha.emailer import SecureMailer
from uvcreha import jsonschema
from uvcreha.request import Request
from uvcreha.security import SecurityError
from uvcreha.webpush import Webpush


class Routes(NamedRoutes):

    def __init__(self):
        super().__init__(extractor=reiter.view.meta.routables)


@dataclass
class RESTApplication(Application):

    connector: Optional[Connector] = None
    request_factory: horseman.meta.Overhead = Request

    def __call__(self, environ, start_response):
        environ['app'] = self
        if self._caller is not None:
            return self._caller(environ, start_response)
        return super().__call__(environ, start_response)


@dataclass
class Browser(RESTApplication):

    routes: NamedRoutes = field(default_factory=Routes)
    ui: registries.UIRegistry = field(
        default_factory=registries.UIRegistry)

    def check_permissions(self, route, environ):
        if permissions := route.extras.get('permissions'):
            user = environ.get(self.config.env.user)
            if user is None:
                raise SecurityError(None, permissions)
            if not permissions.issubset(user.permissions):
                raise SecurityError(user, permissions - user.permissions)


api = RESTApplication(name='REST Application')
browser = Browser(name='Browser Application')
