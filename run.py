import os
import hydra
import logging
import functools
import pathlib
import contextlib
import colorlog
from horseman.prototyping import WSGICallable


CWD = pathlib.Path(__file__).parent.resolve()


@contextlib.contextmanager
def environment(**environ):
    """Temporarily set the process environment variables.
    """
    def cast_items(mapping):
        for k, v in mapping.items():
            v = str(v)
            if v.startswith('path:'):
                path = pathlib.Path(v[5:]).resolve()
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


def hydra_environ(*args, **kwargs):

    def temporary_environ(func):
        @functools.wraps(func)
        @hydra.main(*args, **kwargs)
        def hydra_conf_environ_wrapper(config):
            with environment(**config.environ):
                return func(config)

        return hydra_conf_environ_wrapper
    return temporary_environ


def webpush_plugin(config):
    from collections import namedtuple

    webpush = namedtuple(
        'Webpush', [
            'vapid_claims',
            'vapid_private_key',
            'vapid_public_key',
        ])

    with (CWD / pathlib.Path(config.private_key)).open() as fd:
        vapid_private_key = fd.readline().strip("\n")

    with (CWD / pathlib.Path(config.public_key)).open() as fd:
        vapid_public_key = fd.readline().strip("\n")

    return webpush(
        vapid_private_key=vapid_private_key,
        vapid_public_key=vapid_public_key,
        vapid_claims=config.vapid_claims
    )


def make_logger(config) -> logging.Logger:
    logger = colorlog.getLogger(config.name)
    logger.setLevel(logging.DEBUG)
    return logger


def api(config, database, webpush):
    from docmanager.app import api as app
    app.database = database
    app.config.update(config)
    app.plugins.register(webpush, name="webpush")
    return app


def browser(config, database, webpush):
    from docmanager.db import User
    from docmanager.mq import AMQPEmitter
    from docmanager.auth import Auth
    from docmanager.app import browser as app

    def fanstatic_middleware(config) -> WSGICallable:
        from fanstatic import Fanstatic
        return functools.partial(Fanstatic, **config)


    def session_middleware(config) -> WSGICallable:
        import cromlech.session
        import cromlech.sessions.file

        folder = pathlib.Path("/tmp/sessions")
        handler = cromlech.sessions.file.FileStore(folder, 3000)
        manager = cromlech.session.SignedCookieManager(
            "secret", handler, cookie="my_sid")
        return cromlech.session.WSGISessionManager(
            manager, environ_key=config.session)

    app.database = database
    app.config.update(config.app)

    app.plugins.register(webpush, name="webpush")

    auth = Auth(User(database.session), config.app.env)
    app.plugins.register(auth, name="authentication")
    app.middlewares.register(auth, order=0)  # very first.

    amqp = AMQPEmitter(config.amqp)
    app.plugins.register(amqp, name="amqp")

    app.middlewares.register(
        session_middleware(config.app.env), order=1)

    app.middlewares.register(
        fanstatic_middleware(config.app.assets), order=2)

    return app


@hydra_environ(config_name="config.yaml")
def run(config):
    import bjoern
    import importscan

    import docmanager
    import docmanager.db
    import docmanager.mq
    import uvcreha.example
    import uvcreha.example.app
    from rutter.urlmap import URLMap

    importscan.scan(docmanager)
    importscan.scan(uvcreha.example)

    database = docmanager.db.Database(**config.arango)
    webpush = webpush_plugin(config.app.webpush)
    app = URLMap()
    app['/'] = browser(config, database, webpush)
    app['/api'] = api(config, database, webpush)

    # Serving the app
    AMQPworker = docmanager.mq.Worker(app, config.amqp)
    try:
        AMQPworker.start()

        logging.info(
            "Server started on "
            f"http://{config.server.host}:{config.server.port}")

        bjoern.run(
            app, config.server.host,
            int(config.server.port), reuse_port=True)
    except KeyboardInterrupt:
        pass
    finally:
        AMQPworker.stop()

if __name__ == "__main__":
    run()
