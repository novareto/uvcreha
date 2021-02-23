import os
import logging
import functools
import pathlib
import contextlib
import colorlog
from typing import Type
from fanstatic import Fanstatic
from omegaconf import OmegaConf
from reiter.application.startup import environment, make_logger
from horseman.prototyping import WSGICallable
from zope.dottedname import resolve


def fanstatic_middleware(config) -> WSGICallable:
    return functools.partial(Fanstatic, **config)


def session_middleware(config) -> WSGICallable:
    import cromlech.session
    import cromlech.sessions.file

    handler = cromlech.sessions.file.FileStore(
        config.session.cache, 3000
    )
    manager = cromlech.session.SignedCookieManager(
        config.session.cookie_secret,
        handler,
        cookie=config.session.cookie_name
    )
    return cromlech.session.WSGISessionManager(
        manager, environ_key=config.env.session)


def start(config):
    # Dramatiq
    import dramatiq
    from dramatiq.brokers.rabbitmq import RabbitmqBroker
    broker = RabbitmqBroker(host="localhost", virtual_host="/")
    broker.declare_queue("default")
    dramatiq.set_broker(broker)


    import bjoern
    import importscan
    import uvcreha
    import uvcreha.mq
    import uvcreha.tasker
    from uvcreha.startup import Applications
    from rutter.urlmap import URLMap

    importscan.scan(uvcreha)

    logger = make_logger("uvcreha")
    apps = Applications.from_configuration(config, logger=logger)

    apps.browser.register_middleware(
        fanstatic_middleware(config.app.assets), order=0)  # very first.

    apps.browser.register_middleware(
        session_middleware(config.app), order=1)

    app = URLMap()
    app['/'] = apps.browser
    app['/api'] = apps.api

    # Serving the app
    AMQPworker = uvcreha.mq.Worker(apps, config.amqp)
    tasker = uvcreha.tasker.Tasker(apps)

    apps.browser.utilities.register(tasker, name="tasker")
    apps.api.utilities.register(tasker, name="tasker")

    # Dramatiq worker
    dramatiq_worker = dramatiq.Worker(broker, queues=['default'])

    try:
        AMQPworker.start()
        tasker.start()
        dramatiq_worker.start()

        if not config.server.socket:
            logger.info(
                "Server started on "
                f"http://{config.server.host}:{config.server.port}")

            bjoern.run(
                app, config.server.host,
                int(config.server.port), reuse_port=True)
        else:
            logger.info(
                f"Server started on socket {config.server.socket}.")

            bjoern.run(app, config.server.socket)

    except KeyboardInterrupt:
        pass
    finally:
        AMQPworker.stop()
        tasker.stop()
        dramatiq_worker.stop()


def resolve_path(path: str) -> str:
    path = pathlib.Path(path)
    return str(path.resolve())


def resolve_class(path: str) -> Type:
    return resolve.resolve(path)


if __name__ == "__main__":
    OmegaConf.register_resolver("path", resolve_path)
    OmegaConf.register_resolver("class", resolve_class)
    baseconf = OmegaConf.load('config.yaml')
    override = OmegaConf.from_cli()
    config = OmegaConf.merge(baseconf, override)
    with environment(**config.environ):
        start(config)
