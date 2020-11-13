import asyncio
import logging
import threading
import aioamqp
import aioarangodb
from contextlib import asynccontextmanager


class Receiver:

    def __init__(self, config):
        self.config = config
        self.event_loop = asyncio.new_event_loop()
        self._thread = threading.Thread(target=self._run)

    @asynccontextmanager
    async def arango_connection(self):
        client = aioarangodb.ArangoClient(hosts=self.config.url)
        db = await client.db(
            self.config.database,
            username=self.config.user,
            password=self.config.password
        )
        try:
            yield db
        finally:
            await client.close()

    async def handle_message(self, channel, body, envelope, properties):
        async with self.arango_connection() as db:
            # we had a DB connection now.
            print('CONNECTED !!')
        await channel.basic_client_ack(delivery_tag=envelope.delivery_tag)

    async def worker(self):
        logging.info('Started AMQP messaging worker.')
        try:
            transport, protocol = await aioamqp.connect()
        except aioamqp.AmqpClosedConnection:
            print("closed connections")
            return

        channel = await protocol.channel()
        await channel.exchange(
            exchange_name='messages',
            type_name='fanout'
        )
        result = await channel.queue(queue_name='', exclusive=True)
        queue_name = result['queue']
        await channel.queue_bind(
            exchange_name='messages',
            queue_name=queue_name,
            routing_key=''
        )
        while True:
            await channel.basic_consume(
                self.handle_message, queue_name=queue_name)

    def _run(self):
        try:
            self.event_loop.run_until_complete(self.worker())
        except RuntimeError as exc:
            # was cancelled.
            pass

    def _shutdown(self):
        logging.info('received stop signal, cancelling tasks...')
        self.event_loop.stop()
        while self.event_loop.is_running():
            pass
        self.event_loop.close()
        logging.info('bye, exiting in a minute...')

    def start(self):
        return self._thread.start()

    def stop(self):
        self._shutdown()
        return self._thread.join()
