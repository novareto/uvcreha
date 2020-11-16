import threading
from kombu.mixins import ConsumerMixin
from kombu import Exchange, Queue, Connection as AMQPConnection


class Worker(ConsumerMixin):

    def __init__(self, app, config, logger):
        self.config = config
        self.connection = None
        self.app = app
        self.logger = logger
        self.exchange = Exchange('object_events', type='topic')
        self.queues = dict(
            add_q=Queue(
                'add', self.exchange, routing_key='object.add'),
            del_q=Queue(
                'delete', self.exchange, routing_key='object.delete'),
            upd_q=Queue(
                'update', self.exchange, routing_key='object.update'),
        )

    def get_consumers(self, Consumer, channel):
        return [Consumer(
            (self.queues['add_q'], self.queues['upd_q']),
            accept=['pickle', 'json'],
            callbacks=[self.on_message]
        )]

    def on_message(self, body, message):
        self.logger.info("Got task body: %s", body)
        self.logger.info("Got task Message: %s", message)
        message.ack()

    def runner(self):
        with AMQPConnection(self.config.url) as conn:
            try:
                self.connection = conn
                self.run()
            except:
                self.logger.info('Quitting the AMQP listener')
        self.connection = None

    @classmethod
    def start(cls, app, config, logger):
        worker = cls(app, config, logger)
        thread = threading.Thread(target=worker.runner)
        thread.start()
        return thread
