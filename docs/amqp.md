# Services mit AMQP

In uvcreha können wir einfach AMQP Nachrichten senden und empfangen.


# Empfangen

```python
from reiter.amqp.mq import AMQP
from reiter.amqp.meta import CustomConsumer
from reiter.startup.utils import make_logger


@AMQP.consumer
class TestConsumer(CustomConsumer):

    queues = ['add', 'update']
    accept = ['pickle', 'json']

    def __call__(self, body, message):
        logging = make_logger('Consumer')
        logging.info("Got task body: %s", body)
        logging.debug("Got task Message: %s", message)
        message.ack()
```

# Senden

```python
# TODO
```
