from uvcreha.app import browser, api
from uvcreha.models import User, MessagingType
from roughrider.events.dispatcher import Dispatcher


class MessageCenter(Dispatcher):
    default: MessagingType = MessagingType.email

    def dispatch(self, request, uid, **kwargs):
        user = request.database(User).fetch(uid)
        if user.preferences is not None:
            return user.preferences.messaging_type.name
        print(f'User {user.id} has no preference.')
        return self.default.name


message_center = MessageCenter()


@message_center.subscribe(MessagingType.email.name)
def email_messaging(request, uid, message, **kwargs):
    print('I am emailing : ', request, uid, message)


@message_center.subscribe(MessagingType.webpush.name)
def webpush_messaging(request, uid, message, **kwargs):
    print('Webpush sending : ', request, uid, message)
