import os
import hydra
import logging
import functools
from pathlib import Path
import contextlib
import colorlog
from horseman.prototyping import WSGICallable


current_path = Path(__file__).parent


@contextlib.contextmanager
def environment(**environ):
    """Temporarily set the process environment variables.
    """
    def cast_items(mapping):
        for k, v in mapping.items():
            v = str(v)
            if v.startswith('path:'):
                path = Path(v[5:]).resolve()
                path.mkdir(parents=True, exist_ok=True)
                yield k, str(path)
            else:
                yield k, v

    old_environ = dict(os.environ)
    os.environ.update(dict(cast_items(environ)))
    try:
        yield
    finally:
        os.environ.clear()
        os.environ.update(old_environ)


def temporary_environ(func):

    @functools.wraps(func)
    def hydra_conf_environ_wrapper(config):
        with environment(**config.environ):
            return func(config)

    return hydra_conf_environ_wrapper


def fanstatic_middleware(config) -> WSGICallable:
    from fanstatic import Fanstatic
    from functools import partial

    return partial(Fanstatic, **config)


def session_middleware(config) -> WSGICallable:
    import cromlech.session
    import cromlech.sessions.file

    folder = Path("/tmp/sessions")
    print(folder.absolute())
    handler = cromlech.sessions.file.FileStore(folder, 3000)
    manager = cromlech.session.SignedCookieManager(
        "secret", handler, cookie="my_sid")
    return cromlech.session.WSGISessionManager(
        manager, environ_key=config.session)


def make_logger(config) -> logging.Logger:
    logger = colorlog.getLogger(config.name)
    logger.setLevel(logging.DEBUG)
    return logger


@hydra.main(config_name="config.yaml")
@temporary_environ
def run(config):
    import bjoern
    import importscan

    import docmanager
    import docmanager.app
    import docmanager.db
    import docmanager.auth
    import docmanager.flash

    import uvcreha.example
    import uvcreha.example.app

    importscan.scan(docmanager)
    importscan.scan(uvcreha.example)

    database = docmanager.db.Database(**config.app.arango)
    app = docmanager.app.application
    app.setup(
        config=config.app,
        database=database,
        logger=make_logger(config.app.logger),
        request_factory=uvcreha.example.app.CustomRequest
    )

    # Plugins
    flash = docmanager.flash.Flash()
    auth = docmanager.auth.Auth(
        docmanager.db.User(database.session), config.app.env)

    app.plugins.register(auth, name="authentication")
    app.plugins.register(flash, name="flash")

    # Middlewares
    app.middlewares.register(
        session_middleware(config.app.env), priority=1)
    app.middlewares.register(
        fanstatic_middleware(config.app.assets), priority=0)
    app.middlewares.register(auth, priority=2)

    # Serving the app
    app.logger.info(
        "Server started on "
        f"http://{config.server.host}:{config.server.port}")

    bjoern.run(
        app, config.server.host,
        int(config.server.port), reuse_port=True)

if __name__ == "__main__":
    run()
