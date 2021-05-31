import uvcreha.auth.filters
from omegaconf import OmegaConf
from rutter.urlmap import URLMap
from reiter.amqp.emitter import AMQPEmitter
from roughrider.storage.meta import StorageCenter
from uvcreha.app import api, browser
from uvcreha.emailer import SecureMailer
from uvcreha.database import Connector
from uvcreha.auth import Auth
from uvcreha.auth.utilities import TwoFA
from uvcreha import plugins
from uvcreha.workflow import user_workflow


def setup(config: OmegaConf):

    # browser application
    browser.config.update(config.app)
    browser.connector = Connector.from_config(**config.arango)
    browser.request = config.app.factories.request

    auth = Auth(browser.connector, config.app.env, filters = [
        uvcreha.auth.filters.security_bypass({'/login'}),
        uvcreha.auth.filters.secured('/login'),
        uvcreha.auth.filters.filter_user_state({
            user_workflow.states.inactive,
            user_workflow.states.closed
        }),
        uvcreha.auth.filters.TwoFA('/2FA'),
    ])

    # middlewares
    browser.register_middleware(
        plugins.fanstatic_middleware(config.app.assets), order=10)
    browser.register_middleware(
        plugins.session_middleware(config.app), order=20)
    browser.register_middleware(auth, order=30)

    # Utilities
    browser.utilities.register(auth, name="authentication")
    browser.utilities.register(TwoFA(config.app.env), name="twoFA")
    browser.utilities.register(AMQPEmitter(config.amqp), name="amqp")
    browser.utilities.register(StorageCenter(), name="storage")

    # api application
    api.config.update(config.app)
    api.connector = Connector.from_config(**config.arango)
    api.request = api.config.factories.request

    # Common utilities
    if config.emailer:
        emailer = SecureMailer(config.emailer)
        api.utilities.register(emailer, name="emailer")
        browser.utilities.register(emailer, name="emailer")

    if config.webpush:
        webpush = plugins.webpush_plugin(config.webpush)
        api.utilities.register(webpush, name="webpush")
        browser.utilities.register(webpush, name="webpush")

    if config.twilio:
        twilio = plugins.twilio_plugin(config.twilio)
        api.utilities.register(twilio, 'twilio')
        browser.utilities.register(twilio, 'twilio')

    app = URLMap()
    app['/'] = browser
    app['/api'] = api

    return app
