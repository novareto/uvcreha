# Services mit AMQP

In uvcreha können wir einfach AMQP Nachrichten senden und empfangen.


# Config entry

```yaml
amqp: !new:reiter.amqp.mq.AMQPCenter
  - queue_name: !new:kombu.Queue
      name: queue_identifier
      routing_key: my_routing_key
      exchange: !new:kombu.Exchange
        name: my_topical_name
        type: topic
  - !name:python.path.to.MyCustomConsumer
```

if we have several queues, we can declare the exchange globally

```yaml
mq_exhange: !new:kombu.Exchange
  name: my_topical_name
  type: topic

amqp: !new:reiter.amqp.mq.AMQPCenter
  - queue_name: !new:kombu.Queue
      name: queueid
      routing_key: my_routing_key
      exchange: !ref <mq_exhange>
    other_queue: !new:kombu.Queue
      name: queue2id
      routing_key: some_other_key
      exchange: !ref <mq_exhange>
  - !name:python.path.to.MyCustomConsumer
  - !name:python.path.to.MyOtherCustomConsumer
```


# Empfangen

```python
from reiter.amqp.meta import CustomConsumer


class MyConsumer(CustomConsumer):

    queues = ['queue_name']
    accept = ['json']

    def __call__(self, body: dict, message):
        pass
```
