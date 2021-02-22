import asyncio
import logging
import threading
import collections


class Tasker:

    def __init__(self, app):
        self.app = app
        self.loop = None
        self._thread = threading.Thread(target=self.run)
        self.tasks = collections.deque()

    def enqueue(self, task):
        result = asyncio.run_coroutine_threadsafe(task, self.loop)
        self.tasks.append(result)
        return result

    def run(self):
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        try:
            self.loop.run_forever()
        finally:
            try:
                shutdown_asyncgens = self.loop.shutdown_asyncgens()
            except AttributeError:
                pass
            else:
                self.loop.run_until_complete(shutdown_asyncgens)
            self.loop.close()
            asyncio.set_event_loop(None)

    def start(self):
        logging.info('Starting tasker.')
        return self._thread.start()

    def stop(self):
        logging.info('Stopping tasker.')
        self.loop.call_soon_threadsafe(self.loop.stop)
        self._thread.join()
