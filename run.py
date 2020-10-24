import hydra
import hydra.utils
import logging
import bjoern
import fanstatic
import functools
import pathlib
import fanstatic
import rutter.urlmap
import horseman.response
import cromlech.session
import cromlech.sessions.file

from docmanager.db import Database, create_graph
import docmanager.app
import docmanager.types
import docmanager.auth


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


def auth_middleware(config):
    auth = docmanager.auth.Auth(config.app.env.session, login_path="/login")
    return auth


@hydra.main(config_path="config.yaml")
def run(config):

    database = Database(**config.app.db)
    create_graph(database)

    docmanager.app.application.set_configuration(config.app)
    docmanager.app.application.set_database(database)
    docmanager.app.application.register_middleware(
        session_middleware(config.app.env))
    docmanager.app.application.register_middleware(
        fanstatic_middleware(config.app.assets))

    docmanager.app.application.register_middleware(
        auth_middleware(config),
        order=10
    )
    # Serving the app
    server = config.server
    host, port = server.host, server.port
    docmanager.app.application.logger.info(
        f"Server Started on http://{host}:{port}")
    bjoern.run(docmanager.app.application,
               host, int(port), reuse_port=True)


if __name__ == "__main__":
    run()
