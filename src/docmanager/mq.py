import threading
import abc
import logging
from typing import Dict, List, Callable, ClassVar, Optional
from kombu.mixins import ConsumerMixin
from kombu import Exchange, Queue, Connection as AMQPConnection


class CustomConsumer(abc.ABC):
    queues: ClassVar[List[str]]
    accept: ClassVar[List[str]]

    def __init__(self, app):
        self.app = app

    @abc.abstractmethod
    def __call__(self, body, message):
        pass


class AMQPCenter:

    exchange: Exchange = Exchange('object_events', type='topic')
    consumers: List[CustomConsumer]
    queues: Dict[str, Queue] = {
        'add': Queue(
            'add', exchange, routing_key='object.add'),
        'delete': Queue(
            'delete', exchange, routing_key='object.delete'),
        'update': Queue(
            'update', exchange, routing_key='object.update'),
    }

    def __init__(self, *consumers):
        self._consumers = list(consumers)

    def consumer(self, consumer: CustomConsumer):
        self._consumers.append(consumer)
        return consumer

    def consumers(self, app, cls, channel):
        for consumer in self._consumers:
            yield cls(
                [self.queues[q] for q in consumer.queues],
                accept=consumer.accept,
                callbacks=[consumer(app)]
            )


AMQP = AMQPCenter()


@AMQP.consumer
class TestConsumer(CustomConsumer):

    queues = ['add', 'update']
    accept = ['pickle', 'json']

    def __call__(self, body, message):
        logging.info("Got task body: %s", body)
        logging.info("Got task Message: %s", message)
        message.ack()


class Worker(ConsumerMixin):

    connection: Optional[AMQPConnection] = None

    def __init__(self, app, config, amqpcenter: AMQPCenter = AMQP):
        self.app = app
        self.config = config
        self.amqpcenter = amqpcenter
        self.thread = threading.Thread(target=self.runner)

    def get_consumers(self, Consumer, channel):
        consumers = list(
            self.amqpcenter.consumers(self.app, Consumer, channel))
        return consumers

    def runner(self):
        try:
            with AMQPConnection(self.config.url) as conn:
                self.connection = conn
                self.run()
        finally:
            self.connection = None

    def start(self):
        self.thread.start()

    def stop(self):
        self.should_stop = True
        logging.info("Quitting MQ thread.")
        self.thread.join()
