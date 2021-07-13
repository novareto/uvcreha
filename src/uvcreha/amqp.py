import logging
from horseman.http import HTTPError
from reiter.amqp.meta import CustomConsumer
from uvcreha import contenttypes
from jsonschema_rs import ValidationError


class UserCreationConsumer(CustomConsumer):

    queues = ['user_new']
    accept = ['json']

    def __call__(self, body: dict, message):
        ct = contenttypes.registry['user']
        try:
            ct.validate(body)
        except ValidationError as exc:
            logging.error(str(exc))
        else:
            db = self.context['app'].utilities["arango"].get_database()
            binding = ct.bind(db)
            try:
                binding.create(_key=body['uid'], **body)
            except HTTPError as exc:
                logging.error(exc.body)
        finally:
            message.ack()
