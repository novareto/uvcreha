from kombu.pools import producers

from kombu import Exchange


task_exchange = Exchange("object_events", type="topic")


def send_as_task(connection, fun, args=(), kwargs={}, rk="object."):
    payload = {"fun": fun, "args": args, "kwargs": kwargs}

    with producers[connection].acquire(block=True) as producer:
        producer.publish(
            payload,
            serializer="json",
            exchange=task_exchange,
            declare=[task_exchange],
            routing_key=rk,
        )


if __name__ == "__main__":
    from kombu import Connection

    connection = Connection("amqp://guest:guest@localhost:5672//")
    send_as_task(
        connection, fun="hello_task",
        args=("Kombu",), kwargs={}, rk="object.add"
    )
    send_as_task(
        connection, fun="hello_task",
        args=("Kombu",), kwargs={}, rk="object.update"
    )
