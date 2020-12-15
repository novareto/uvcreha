from collections import defaultdict
from dataclasses import dataclass, field
from functools import partial
from typing import Mapping, Optional

import horseman.meta
import horseman.response
import horseman.http
from reiter.arango.connector import Connector
from reiter.arango.validation import ValidationError
from reiter.routing.routes import Routes
from docmanager import registries
from docmanager.security import SecurityError
from docmanager.request import Request
from omegaconf.dictconfig import DictConfig


@dataclass
class Router(horseman.meta.APINode):

    config: Mapping = field(default_factory=partial(DictConfig, {}))
    connector: Optional[Connector] = None
    middlewares: list = field(default_factory=registries.PriorityList)
    plugins: Mapping = field(default_factory=registries.NamedComponents)
    request_factory: horseman.meta.Overhead = Request
    routes: Routes = field(default_factory=Routes)
    subscribers: dict = field(default_factory=partial(defaultdict, list))

    def route(self, *args, **kwargs):
        return self.routes.register(*args, **kwargs)

    def check_permissions(self, route, environ):
        pass

    def notify(self, event_name: str, *args, **kwargs):
        for subscriber in self.subscribers[event_name]:
            if (result := subscriber(*args, **kwargs)):
                return result

    def subscribe(self, event_name: str):
        def wrapper(func):
            self.subscribers[event_name].append(func)
        return wrapper

    def resolve(self, path, environ):
        route = self.routes.match(
            environ['REQUEST_METHOD'], path)
        if route is not None:
            self.notify('route_found', self, route, environ)
            self.check_permissions(route, environ)
            environ['horseman.path.params'] = route.params
            request = self.request_factory(self, environ, route)
            self.notify('request_created', self, request)
            return route.endpoint(request, **route.params)
        return None

    def __call__(self, environ, start_response):
        try:
            caller = super().__call__
            for order, middleware in self.middlewares:
                caller = middleware(caller)
            return caller(environ, start_response)
        except ValidationError as exc:
            return exc(environ, start_response)


@dataclass
class Browser(Router):

    ui: registries.UIRegistry = field(
        default_factory=registries.UIRegistry)

    def check_permissions(self, route, environ):
        if permissions := route.extras.get('permissions'):
            user = environ.get(self.config.env.user)
            if user is None:
                raise SecurityError(None, permissions)
            if not permissions.issubset(user.permissions):
                raise SecurityError(user, permissions - user.permissions)


browser = Browser()
api = Router()
