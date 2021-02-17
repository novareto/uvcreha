import typing

from horseman.prototyping import WSGICallable
from reiter.arango.connector import Connector
from reiter.application.app import Application

import docmanager.plugins
import docmanager.api.user
from docmanager.models import User
from docmanager.mq import AMQPEmitter
from docmanager.auth import Auth
from docmanager.app import browser, api
from docmanager.webpush import Webpush
from docmanager.emailer import SecureMailer


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
    User = config.app.factories.user
    browser.connector = connector
    browser.config.update(config.app)
    db = connector.get_database()
    auth = Auth(db(User), config.app.env)
    browser.utilities.register(auth, name="authentication")
    browser.register_middleware(auth, order=2)

    browser.utilities.register(AMQPEmitter(config.amqp), name="amqp")
    browser.utilities.register(webpush, name="webpush")
    browser.utilities.register(emailer, name="emailer")
    return browser


class Applications(typing.NamedTuple):
    api: Application
    browser: Application

    @classmethod
    def from_configuration(cls, config, logger=None):
        connector = Connector(**config.arango)
        webpush = webpush_plugin(config.webpush)
        emailer = SecureMailer(config.emailer)
        apps = cls(
            api=create_api(
                config, connector, webpush, emailer),
            browser=create_browser(
                config, connector, webpush, emailer)
        )
        docmanager.plugins.load(logger=logger)
        return apps
