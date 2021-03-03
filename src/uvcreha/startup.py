import typing
import functools
import fanstatic

import cromlech.session
import cromlech.sessions.file
from horseman.prototyping import WSGICallable
from reiter.arango.connector import Connector
from reiter.application.app import Application

import uvcreha.plugins
import uvcreha.api.user
from uvcreha.mq import AMQPEmitter
from uvcreha.auth import Auth
from uvcreha.app import api, backend, browser
from uvcreha.webpush import Webpush
from uvcreha.emailer import SecureMailer


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


def create_api(config, connector, webpush, emailer) -> WSGICallable:
    api.connector = connector
    api.config.update(config)
    api.utilities.register(webpush, name="webpush")
    api.utilities.register(emailer, name="emailer")
    return api


def create_browser(config, connector, webpush, emailer) -> WSGICallable:
    browser.connector = connector
    browser.request = config.app.factories.request
    browser.config.update(config.app)
    db = connector.get_database()
    auth = Auth(db(config.app.factories.user), config.app.env)

    # utilities
    browser.utilities.register(auth, name="authentication")
    browser.utilities.register(AMQPEmitter(config.amqp), name="amqp")
    browser.utilities.register(webpush, name="webpush")
    browser.utilities.register(emailer, name="emailer")

    # middlewares
    browser.register_middleware(
        fanstatic_middleware(config.app.assets), order=0)  # very first.

    browser.register_middleware(
        session_middleware(config.app), order=1)

    browser.register_middleware(auth, order=2)

    return browser


def create_backend(config, connector) -> WSGICallable:
    backend.connector = connector
    backend.request = config.app.factories.request
    backend.config.update(config.app)
    db = connector.get_database()
    auth = Auth(db(config.app.factories.user), config.app.env)

    # utilities
    backend.utilities.register(auth, name="authentication")

    # middlewares
    backend.register_middleware(
        fanstatic_middleware(config.app.assets), order=0)  # very first.

    backend.register_middleware(
        session_middleware(config.app), order=1)

    backend.register_middleware(auth, order=2)

    return backend


class Applications(typing.NamedTuple):
    api: Application
    backend: Application
    browser: Application

    @classmethod
    def from_configuration(cls, config, logger=None):
        connector = Connector(**config.arango)
        webpush = webpush_plugin(config.webpush)
        emailer = SecureMailer(config.emailer)
        apps = cls(
            api=create_api(config, connector, webpush, emailer),
            backend=create_backend(config, connector),
            browser=create_browser(config, connector, webpush, emailer)
        )
        uvcreha.plugins.load(logger=logger)
        return apps
