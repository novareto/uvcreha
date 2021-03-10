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
from horseman.prototyping import WSGICallable
from reiter.application.app import Application
from reiter.application.browser import registries
from reiter.amqp.emitter import AMQPEmitter
from reiter.arango.connector import Connector
from reiter.arango.validation import ValidationError
from roughrider.routing.route import NamedRoutes
from uvcreha.auth import Auth
from uvcreha.emailer import SecureMailer
from uvcreha.request import Request
from uvcreha.security import SecurityError
from uvcreha.webpush import Webpush


def fanstatic_middleware(config) -> WSGICallable:
    return functools.partial(fanstatic.Fanstatic, **config)


def session_middleware(config) -> WSGICallable:
    handler = cromlech.sessions.file.FileStore(
        config.session.cache, 3000
    )
    manager = cromlech.session.SignedCookieManager(
        config.session.cookie_secret,
        handler,
        cookie=config.session.cookie_name
    )
    return cromlech.session.WSGISessionManager(
        manager, environ_key=config.env.session)


def webpush_plugin(config):

    with open(config.private_key) as fd:
        private_key = fd.readline().strip("\n")

    with open(config.public_key) as fd:
        public_key = fd.read().strip("\n")

    return Webpush(
        private_key=private_key,
        public_key=public_key,
        claims=config.vapid_claims
    )


class Routes(NamedRoutes):

    def __init__(self):
        super().__init__(extractor=reiter.view.meta.routables)


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

    def configure(self, config):
        self.config.update(config.app)
        self.connector = Connector(**config.arango)
        self.request = self.config.factories.request

        # Utilities
        if config.emailer:
            emailer = SecureMailer(config.emailer)
            self.utilities.register(emailer, name="emailer")

        if config.webpush:
            webpush = webpush_plugin(config.webpush)
            self.utilities.register(webpush, name="webpush")


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

    def configure(self, config):
        self.config.update(config.app)
        self.connector = Connector(**config.arango)
        self.request = self.config.factories.request

        # utilities
        db = self.connector.get_database()
        auth = Auth(db(self.config.factories.user), self.config.env)
        self.utilities.register(auth, name="authentication")
        self.utilities.register(AMQPEmitter(config.amqp), name="amqp")

        if config.emailer:
            emailer = SecureMailer(config.emailer)
            self.utilities.register(emailer, name="emailer")

        if config.webpush:
            webpush = webpush_plugin(config.webpush)
            self.utilities.register(webpush, name="webpush")

        # middlewares
        self.register_middleware(
            fanstatic_middleware(self.config.assets), order=0)

        self.register_middleware(
            session_middleware(self.config), order=1)

        self.register_middleware(auth, order=2)


api = RESTApplication('REST Application')
browser = Browser('Browser Application')
