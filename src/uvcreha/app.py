import arango
import functools
import fanstatic
import cromlech.session
import cromlech.sessions.file
import horseman.http
import horseman.meta
import horseman.response
import reiter.view.meta

from typing import Optional
from dataclasses import dataclass, field
from horseman.types import WSGICallable
from reiter.application.app import Application
from reiter.application.browser import registries
from roughrider.routing.route import NamedRoutes
from uvcreha.request import Request
from uvcreha.security import SecurityError
from reiter.arango.connector import Connector


class Routes(NamedRoutes):

    def __init__(self):
        super().__init__(extractor=reiter.view.meta.routables)


@dataclass
class RESTApplication(Application):

    connector: Optional[Connector] = None
    request_factory: horseman.meta.Overhead = Request


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
