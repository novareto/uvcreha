import hydra


def fanstatic_middleware(config):
    from fanstatic import Fanstatic
    from functools import partial

    return partial(Fanstatic, **config)


def session_middleware(config):
    from pathlib import Path
    import cromlech.session
    import cromlech.sessions.file

    current = Path(__file__).parent
    folder = current / "sessions"
    handler = cromlech.sessions.file.FileStore(folder, 3000)
    manager = cromlech.session.SignedCookieManager(
        "secret", handler, cookie="my_sid")
    return cromlech.session.WSGISessionManager(
        manager, environ_key=config.session)


def make_logger(config):
    import logging
    import colorlog

    logger = colorlog.getLogger(config.name)
    logger.setLevel(logging.DEBUG)
    return logger


@hydra.main(config_name="config.yaml")
def run(config):
    import bjoern
    import importscan

    import docmanager
    import docmanager.app
    import docmanager.db
    import docmanager.auth

    import uvcreha.example
    import uvcreha.example.app

    importscan.scan(docmanager)
    importscan.scan(uvcreha.example)

    database = docmanager.db.Database(**config.app.arango)
    auth = docmanager.auth.Auth(
        docmanager.db.User(database), config.app.env)

    app = docmanager.app.application
    app.setup(
        config=config.app,
        database=database,
        logger=make_logger(config.app.logger),
        request_factory=uvcreha.example.app.CustomRequest
    )

    # Plugins
    app.plugins.register(auth, name="authentication")

    # Middlewares
    app.middlewares.register(
        session_middleware(config.app.env), priority=1)
    app.middlewares.register(
        fanstatic_middleware(config.app.assets), priority=0)
    app.middlewares.register(auth, priority=2)

    # Serving the app
    app.logger.info(
        f"Server started on http://{config.server.host}:{config.server.port}")
    bjoern.run(
        app, config.server.host, int(config.server.port), reuse_port=True)

if __name__ == "__main__":
    run()
