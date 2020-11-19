import re
import logging
from http import HTTPStatus
from dataclasses import dataclass, field
from typing import Callable, Mapping, Optional
from functools import partial, wraps
from omegaconf.dictconfig import DictConfig

import horseman.meta
import horseman.http

from docmanager import registries, db
from docmanager.security import SecurityError
from docmanager.routing import Routes
from docmanager.request import Request
from docmanager.validation import ValidationError


@dataclass
class Router(horseman.meta.APINode):

    config: Mapping = field(default_factory=partial(DictConfig, {}))
    database: Optional[db.Database] = None
    request_factory: horseman.meta.Overhead = Request
    routes: Routes = field(default_factory=Routes)
    plugins: Mapping = field(default_factory=registries.NamedComponents)
    middlewares: list = field(default_factory=registries.PriorityList)

    def route(self, *args, **kwargs):
        return self.routes.register(*args, **kwargs)

    def check_permissions(self, route, environ):
        pass

    def resolve(self, path, environ):
        route = self.routes.match(
            environ['REQUEST_METHOD'], path)
        if route is not None:
            self.check_permissions(route, environ)
            environ['horseman.path.params'] = route.params
            request = self.request_factory(self, environ, route)
            return route.endpoint(request, **route.params)
        return None

    def __call__(self, environ, start_response):
        caller = super().__call__
        for order, middleware in self.middlewares:
            caller = middleware(caller)
        return caller(environ, start_response)


@dataclass
class Browser(Router):

    ui: registries.UIRegistry = field(
        default_factory=registries.UIRegistry)

    def check_permissions(self, route, environ):
        # default_permission = {'app.view'}
        if permissions := route.extras.get('permissions'):
            # permissions.update(default_permission)
            user = environ.get(self.config.env.user)
            if user is None:
                raise SecurityError(None, permissions)
            if not permissions.issubset(user.permissions):
                raise SecurityError(user, permissions - user.permissions)




browser = Browser()
api = Router()
