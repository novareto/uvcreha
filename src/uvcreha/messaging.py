import logging
from reiter.events.meta import Subscribers
from uvcreha.app import events
from uvcreha import contenttypes
import uvcreha.events
from typing import Dict


class UserMessageCenter:

    def __init__(self):
        self._subscribers: Dict[str, Subscribers] = {}

    def subscribe(self, name, event_type):
        def register_subscriber(func):
            if name not in self._subscribers:
                subs = self._subscribers[name] = Subscribers()
            else:
                subs = self._subscribers[name]
            subs.add(event_type, func)
            return func
        return register_subscriber

    def dispatch(self, event):
        if isinstance(event, uvcreha.events.UserEvent):
            if preferences := event.user.get('preferences'):
                return preferences.get('messaging_type', 'email')
            return 'email'

    def __call__(self, event):
        key = self.dispatch(event)
        if key is not None and key in self._subscribers:
            self._subscribers[key].notify(event)


message_center = UserMessageCenter()
events.subscribe(uvcreha.events.UserEvent)(message_center)
