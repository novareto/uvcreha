import hydra
import hydra.utils
import logging
import bjoern
import fanstatic
import pathlib
import transaction
import importscan
import rutter.urlmap
import horseman.response
import cromlech.session
import cromlech.sessions.file

from adhoc.db import Database, User, Message
from adhoc.utils.emailer import SecureMailer
from adhoc.utils.storage import Storage
from adhoc.utils.request import Request
from adhoc.utils.tales import tales_expressions

import adhoc.apps.auth
import adhoc.apps.saml
import adhoc.apps.root
import adhoc.apps.root.example_form
import adhoc.apps.management
import adhoc.models
import roughrider.zodb


logger = logging.getLogger(__name__)


def setup_app(config, logger):

    # Preparing the overhead
    request_factory = Request.factory(session_key="sess")
    zodb = roughrider.zodb.ZODB(dict(config.zodb))

    # Add some data
    with zodb.database('main') as db:
        if not hasattr(db.root, 'users'):
            container = db.root.users = adhoc.models.Container()
            container['test'] = adhoc.models.User(username='test',
                                                  password='test')

    # Web frontend
    frontend = adhoc.apps.root.Application(logger, request_factory, config)

    # Auth middleware
    auth = adhoc.apps.auth.Auth(zodb, "sess", login_path="/auth/login")

    # Creating the main router
    application = rutter.urlmap.URLMap(
        not_found_app=horseman.response.Response.create(404)
    )
    application["/"] = zodb.middleware(auth(frontend))
    application["/auth"] = adhoc.apps.auth.AuthNode(
        auth, logger, request_factory)
    return application


def setup_middleware(config):
    # Session middleware
    current = pathlib.Path(__file__).parent
    folder = current / "sessions"
    handler = cromlech.sessions.file.FileStore(folder, 300)
    manager = cromlech.session.SignedCookieManager(
        "secret", handler, cookie="my_sid")
    return cromlech.session.WSGISessionManager(manager, environ_key="sess")


@hydra.main(config_path="config.yaml")
def run(config):
    application = setup_app(config, logger)
    session_middleware = setup_middleware(config)

    # Serving the app
    server = config.server
    host, port = server.host, server.port
    logger.info(f"Server Started on http://{host}:{port}")
    bjoern.run(
        fanstatic.Fanstatic(session_middleware(application)),
        host, int(port), reuse_port=True,
    )


if __name__ == "__main__":
    run()
