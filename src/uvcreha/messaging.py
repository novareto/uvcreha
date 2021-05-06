#from
from uvcreha.app import browser, api
from uvcreha.models import User, MessagingType
from roughrider.events.dispatcher import Dispatcher


class MessageCenter(Dispatcher):
    default: MessagingType = (MessagingType.email.name,)

    def dispatch(self, request, message, uid=None, **kwargs):
        if uid is None:
            user = request.user
        else:
            user = request.database(User).fetch(uid)

        if user.preferences is not None:
            return ([mt.name for mt in user.preferences.messaging_type],
                    user)
        print(f'User {user.id} has no preference.')
        return self.default, user

    def __call__(self, *args, **kwargs):
        keys, user = self.dispatch(*args, **kwargs)
        for key in keys:
            self.notify(key, user, *args, **kwargs)


message_center = MessageCenter()
browser.subscribe('2FA')(message_center)


@message_center.subscribe(MessagingType.email.name)
def email_messaging(user, request, message, **kwargs):
    print('I am emailing : ', request, user.uid, message)


@message_center.subscribe(MessagingType.webpush.name)
def webpush_messaging(user, request, message, **kwargs):
    preferences = user.preferences
    if preferences is not None:
        rr = request.app.utilities['webpush'].send(
            preferences.webpush_subscription, message)
        print(rr)
        print('Webpush sending : ', request, user.uid, message)
    else:
        print('Webpush is not activated for ', user.uid)
