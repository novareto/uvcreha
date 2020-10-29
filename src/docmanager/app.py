import logging
import reg

from http import HTTPStatus

import horseman.meta
from horseman.http import HTTPError

from docmanager import logger
from docmanager.security import SecurityError
from docmanager.routing import Routes
from docmanager.models import ModelsRegistry
from docmanager.db import Database
from docmanager.request import Request
from docmanager.utils.openapi import generate_doc


ROUTER = Routes()


class UIRegistry:

    @reg.dispatch_method(
        reg.match_instance('request'), reg.match_key('name'))
    def layout(self, request, name):
        raise RuntimeError("Unknown layout.")

    def register_layout(self, request, name='default'):
        def add_layout(layout):
            return self.layout.register(
                reg.methodify(layout), request=request, name=name)
        return add_layout

    @reg.dispatch_method(
        reg.match_instance('request'), reg.match_key("name"))
    def slot(self, request, name):
        raise RuntimeError("Unknown slot.")

    def register_slot(self, request, name):
        def add_slot(slot):
            return self.slot.register(
                reg.methodify(slot), request=request, name=name)
        return add_slot


class PluginsRegistry:

    __slots__ = ('_plugins',)

    def __init__(self):
        self._plugins = {}

    def register(self, name, plugin):
        self._plugins.__setitem__(name, plugin)

    def get(self, name):
        return self._plugins.get(name)

    def __len__(self):
        return len(self._plugins)

    def __iter__(self):
        return iter(self._plugins)


class MiddlewaresRegistry:

    __slots__ = ('_middlewares',)

    def __init__(self):
        self._middlewares = []

    def register(self, middleware, order=0):
        self._middlewares.append((order, middleware))

    def __len__(self):
        return len(self._middlewares)

    def __iter__(self):
        def ordered(e):
            return -e[0], repr(e[1])
        yield from (m[1] for m in sorted(self._middlewares, key=ordered))


class Application(dict, horseman.meta.SentryNode, horseman.meta.APINode):

    __slots__ = (
        'config', 'database', 'routes', 'middlewares', 'layout',
        'models', 'request_factory')

    def __init__(self, config=None, database=None,
                 routes=ROUTER, request_factory=Request):
        self.routes = routes
        self.config = config
        self.database = database
        self.request_factory = request_factory
        self.plugins = PluginsRegistry()
        self.middlewares = MiddlewaresRegistry()
        self.models = ModelsRegistry()
        self.ui = UIRegistry()

    @property
    def logger(self):
        return logging.getLogger(self.config.logger.name)

    def check_permissions(self, route, environ):
        #logger.debug("Route %s --> %s" %(route, route.extras.get('permissions')))

        if permissions := route.extras.get('permissions'):
            user = environ.get(self.config.env.user)
            if user is None:
                raise SecurityError(None, permissions)
            if not permissions.issubset(user.permissions):
                raise SecurityError(user, permissions - user.permissions)
        #else:
        #    logger.debug('No Permission for route %s' %route)

    def resolve(self, path_info, environ):
        try:
            route = self.routes.match(
                environ['REQUEST_METHOD'], path_info)
            if route is None:
                return None
            environ['horseman.path.params'] = route.params
            logger.debug("Resolve User %s" % environ.get(self.config.env.user))
            self.check_permissions(route, environ)
            request = self.request_factory(self, environ, route)
            return route.endpoint(request)
        except LookupError:
            raise HTTPError(HTTPStatus.METHOD_NOT_ALLOWED)
        except SecurityError as error:
            if error.user is None:
                raise HTTPError(HTTPStatus.UNAUTHORIZED)
            raise HTTPError(HTTPStatus.FORBIDDEN)

    def handle_exception(self, exc_info, environ):
        exc_type, exc, traceback = exc_info
        self.logger.debug(exc)

    def __call__(self, environ, start_response):
        caller = super().__call__
        for middleware in self.middlewares:
            caller = middleware(caller)
        return caller(environ, start_response)

    def start(self, config):
        self.models.load()
        self.logger.info(
            f"Server Started on http://{config.host}:{config.port}")
        bjoern.run(app, host, int(port), reuse_port=True)


application = Application()
