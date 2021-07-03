import logging
from roughrider.events.dispatcher import Dispatcher
from uvcreha.app import events
from uvcreha import contenttypes


class UserMessageCenter(Dispatcher):

    def dispatch(self, user):
        if preferences := user.get('preferences'):
            return preferences.get('messaging_type', 'email')
        return 'email'

    def __call__(self, request, uid=None, user=None, message=None, **kw):
        if user is None and uid is None:
            logging.info(
                'Dispatcher needs a user or uid to send a message.')
            return
        if message is None:
            logging.info(
                'Dispatcher needs a message to send.')
            return

        if uid is not None and user is None:
            content_type = contenttypes.registry['user']
            binding = content_type.bind(request.database)
            user = binding.find_one(uid=uid)

        key = self.dispatch(user)
        if key is not None:
            self.notify(key, request, user, message)


message_center = UserMessageCenter()
events.subscribe('user_created')(message_center)


@message_center.subscribe('email')
def email_messaging(request, user, message):
    emailer = request.app.utilities['emailer']
    with emailer.smtp() as send:
        msg = emailer.email(
            user['email'], 'Some message', message, html=None)
        send(msg)
