import hydra
import bjoern
import logging
import fanstatic
import functools
import pathlib
import importscan
import fanstatic

import cromlech.session
import cromlech.sessions.file

import docmanager
import docmanager.app
import docmanager.db
import docmanager.auth

import uvcreha.example
import uvcreha.example.app


def fanstatic_middleware(config):
    return functools.partial(fanstatic.Fanstatic, **config)


def session_middleware(config):
    # Session middleware
    current = pathlib.Path(__file__).parent
    folder = current / "sessions"
    handler = cromlech.sessions.file.FileStore(folder, 3000)
    manager = cromlech.session.SignedCookieManager(
        "secret", handler, cookie="my_sid")
    return cromlech.session.WSGISessionManager(
        manager, environ_key=config.session)


@hydra.main(config_path="config.yaml")
def run(config):
    importscan.scan(docmanager)
    importscan.scan(uvcreha.example)

    database = docmanager.db.Database(**config.app.arango)

    app = docmanager.app.application
    app.config = config.app
    app.database = database
    app.request_factory = uvcreha.example.app.CustomRequest
    auth = docmanager.auth.Auth(database, app.models, config.app.env)
    app.plugins.register(auth, name="authentication")

    app.middlewares.register(
        session_middleware(config.app.env), priority=1)
    app.middlewares.register(
        fanstatic_middleware(config.app.assets), priority=0)
    app.middlewares.register(auth, priority=2)

    # Serving the app
    logger = logging.getLogger('docmanager')
    logger.info(
        f"Server started on http://{config.server.host}:{config.server.port}")
    bjoern.run(
        app, config.server.host, int(config.server.port), reuse_port=True)

if __name__ == "__main__":
    run()
