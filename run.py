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


def hydra_environ(*args, **kwargs):

    def temporary_environ(func):
        @functools.wraps(func)
        @hydra.main(*args, **kwargs)
        def hydra_conf_environ_wrapper(config):
            with environment(**config.environ):
                return func(config)

        return hydra_conf_environ_wrapper
    return temporary_environ


def make_logger(config) -> logging.Logger:
    logger = colorlog.getLogger(config.name)
    logger.setLevel(logging.DEBUG)
    return logger


def api(config, database):
    from docmanager.app import api as app
    app.database = database
    app.config.update(config)
    return app


def browser(config, database):
    import docmanager.auth
    import docmanager.mq
    import docmanager.flash
    import docmanager.session
    import docmanager.browser.resources
    from docmanager.app import browser as app

    app.database = database
    app.config.update(config.app)

    app = docmanager.flash.plugin(app, config.app)
    app = docmanager.auth.plugin(app, config.app)
    app = docmanager.session.plugin(app, config.app)
    app = docmanager.browser.resources.plugin(app, config.app)
    app = docmanager.mq.plugin(app, config.amqp)
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
    app = URLMap()
    app['/'] = browser(config, database)
    app['/api'] = api(config, database)

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
