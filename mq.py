import hydra
import logging
from pathlib import Path
import colorlog
from kombu.mixins import ConsumerMixin
from functools import partial

from kombu import Exchange, Queue, Consumer

task_exchange = Exchange('object_events', type='topic')
add_q = Queue('add', task_exchange, routing_key='object.add')
del_q = Queue('delete', task_exchange, routing_key='object.delete')
upd_q = Queue('update', task_exchange, routing_key='object.update')


current_path = Path(__file__).parent


def make_logger(config) -> logging.Logger:
    logger = colorlog.getLogger(config.name)
    logger.setLevel(logging.DEBUG)
    return logger


class MyConsumer(Consumer):

    def receive(self, body, message):
        print('I AM CALLED')
        import pdb; pdb.set_trace()
        print('I AM CALLED')


class Worker(ConsumerMixin):
    def __init__(self, connection, app, logger):
        self.connection = connection
        self.app = app
        self.logger = logger

    def get_consumers(self, Consumer, channel):
        Consumer = partial(MyConsumer, channel, on_decode_error=self.on_decode_error)
        import pdb; pdb.set_trace()
        return [Consumer(queues=[add_q, upd_q ], accept=['pickle', 'json'])]
        # return [
        #     Consumer(
        #         queues=task_queues,
        #         accept=["pickle", "json"],
        #         callbacks=[self.process_task],
        #     )
        # ]

    def process_task(self, body, message):
        self.logger.info("Got task body: %s", body)
        self.logger.info("Got task Message: %s", message)
        message.ack()


@hydra.main(config_name="config.yaml")
def run(config):
    import importscan

    import docmanager
    import docmanager.app
    import docmanager.db
    import docmanager.messaging
    from kombu import Connection

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
        request_factory=uvcreha.example.app.CustomRequest,
    )
    with Connection("amqp://guest:guest@localhost:5672//") as conn:
        try:
            worker = Worker(conn, app, make_logger(config.app.logger))
            worker.run()
        except KeyboardInterrupt:
            print("BYE BYE")


if __name__ == "__main__":
    run()
