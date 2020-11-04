import logging
from http import HTTPStatus

import horseman.meta
import horseman.http

from docmanager import logger, registries
from docmanager.security import SecurityError
from docmanager.routing import Routes
from docmanager.request import Request
from docmanager.validation import ValidationError


class Application(dict, horseman.meta.SentryNode, horseman.meta.APINode):

    def __init__(self, config=None, database=None,
                 routes=None, request_factory=Request):
        if routes is None:
            routes = Routes()
        self.routes = routes
        self.config = config
        self.database = database
        self.request_factory = request_factory

        # Registries
        self.models = registries.ModelsRegistry()
        self.plugins = registries.NamedComponents()
        self.middlewares = registries.PriorityList()
        self.ui = registries.UIRegistry()

    @property
    def logger(self):
        return logging.getLogger(self.config.logger.name)

    def route(self, *args, **kwargs):
        return self.routes.register(*args, **kwargs)

    def check_permissions(self, route, environ):
        if permissions := route.extras.get('permissions'):
            user = environ.get(self.config.env.user)
            if user is None:
                raise SecurityError(None, permissions)
            if not permissions.issubset(user.permissions):
                raise SecurityError(user, permissions - user.permissions)

    def resolve(self, path_info, environ):
        try:
            route = self.routes.match(
                environ['REQUEST_METHOD'], path_info)
            if route is None:
                return None
            environ['horseman.path.params'] = route.params
            logger.debug(
                "Resolve User %s" % environ.get(self.config.env.user))
            self.check_permissions(route, environ)
            request = self.request_factory(self, environ, route)
            return route.endpoint(request, **route.params)
        except LookupError:
            raise horseman.http.HTTPError(HTTPStatus.METHOD_NOT_ALLOWED)
        except SecurityError as error:
            if error.user is None:
                raise horseman.http.HTTPError(HTTPStatus.UNAUTHORIZED)
            raise horseman.http.HTTPError(HTTPStatus.FORBIDDEN)
        except ValidationError as error:
            return error

    def handle_exception(self, exc_info, environ):
        exc_type, exc, traceback = exc_info
        self.logger.debug(exc)

    def __call__(self, environ, start_response):
        caller = super().__call__
        for priority, middleware in reversed(self.middlewares):
            caller = middleware(caller)
        return caller(environ, start_response)


application = Application()
