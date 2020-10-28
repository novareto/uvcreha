import hydra
import logging
import fanstatic
import functools
import pathlib
import importscan
import fanstatic

import cromlech.session
import cromlech.sessions.file
from docmanager.db import Database, create_graph

import docmanager
import docmanager.app
import docmanager.layout
import docmanager.auth

import uvcreha.example
import uvcreha.example.app


def fanstatic_middleware(config):
    return functools.partial(fanstatic.Fanstatic, **config)


def session_middleware(config):
    # Session middleware
    current = pathlib.Path(__file__).parent
    folder = current / "sessions"
    handler = cromlech.sessions.file.FileStore(folder, 300)
    manager = cromlech.session.SignedCookieManager(
        "secret", handler, cookie="my_sid")
    return cromlech.session.WSGISessionManager(
        manager, environ_key=config.session)


@hydra.main(config_path="config.yaml")
def run(config):
    importscan.scan(docmanager)
    importscan.scan(uvcreha.example)

    database = Database(**config.app.db)
    create_graph(database)

    app = docmanager.app.application
    app.database = database
    app.config = config.app
    app.request_factory = CustomRequest
    app.plugins.register(docmanager.auth.Auth(database, config.env))

    app.middlewares.register(
        session_middleware(config.app.env), order=1)
    app.middlewares.register(
        fanstatic_middleware(config.app.assets), order=0)
    app.middlewares.register(auth, order=2)

    # Serving the app
    logger = logging.getLogger('docmanager')
    logger.info(f"Server Started on http://{config.host}:{config.port}")
    bjoern.run(app, host, int(port), reuse_port=True)

if __name__ == "__main__":
    run()
