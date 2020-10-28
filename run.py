
import hydra
import hydra.utils
import logging
import bjoern
import fanstatic
import functools
import pathlib
import importscan
import fanstatic
import rutter.urlmap
import horseman.response
import cromlech.session
import cromlech.sessions.file

from docmanager.db import Database, create_graph
import docmanager
import docmanager.app
import docmanager.types
import docmanager.auth
import docmanager.lf


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

    app = docmanager.app.Application(config=config.app, db=database)
    app['auth'] = auth = docmanager.auth.Auth(app)

    app.middlewares.register(
        session_middleware(config.app.env), order=1)
    app.middlewares.register(
        fanstatic_middleware(config.app.assets), order=0)
    app.middlewares.register(auth, order=2)
    from uvcreha.example.app import CustomRequest
    app.request_factory = CustomRequest

    # Serving the app
    server = config.server
    host, port = server.host, server.port
    app.logger.info(f"Server Started on http://{host}:{port}")
    bjoern.run(app, host, int(port), reuse_port=True)


if __name__ == "__main__":
    run()
