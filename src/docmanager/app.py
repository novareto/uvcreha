import logging
from pathlib import Path

from autoroutes import Routes
import horseman.meta
import horseman.response
import roughrider.routing.node
import roughrider.routing.route
import roughrider.validation.dispatch

from docmanager.layout import template_endpoint
from docmanager.request import Request


class Application(horseman.meta.SentryNode,
                  roughrider.routing.node.RoutingNode):

    __slots__ = ('config', )
    request_factory = Request

    def __init__(self):
        self.routes = Routes()
        self._middlewares = []

    @property
    def logger(self):
        return logging.getLogger(self.config.logger.name)

    def set_configuration(self, config: dict):
        self.config = config

    def register_middleware(self, middleware, order=0):
        self._middlewares.append((order, middleware))

    def route(self, path: str, methods: list=None, **extras):
        def routing(view):
            for fullpath, method, func in \
                roughrider.routing.route.route_payload(
                    path, view, methods):
                payload = {
                    method: roughrider.validation.dispatch.Dispatcher(func),
                    **extras
                }
                self.routes.add(fullpath, **payload)
        return routing

    def middlewares(self):
        def ordered(e):
            return -e[0], repr(e[1])
        yield from (m[1] for m in sorted(self._middlewares, key=ordered))

    def handle_exception(self, exc_info, environ):
        exc_type, exc, traceback = exc_info
        self.logger.debug(exc)

    def __call__(self, environ, start_response):
        caller = super().__call__
        for middleware in self.middlewares():
            caller = middleware(caller)
        return caller(environ, start_response)

application = Application()


@application.route('/', methods=['GET'])
def index(request: Request):
    return horseman.response.reply(200, body='Something')
