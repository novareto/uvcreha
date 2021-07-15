from typing import Any, Optional
from reiter.events.meta import Event
from uvcreha.request import Request
from roughrider.workflow import Transition


class WorkflowTransitionEvent(Event):

    def __init__(self, transition: Transition, obj: Any, **namespace: Any):
        self.transition = transition
        self.obj = obj
        self.namespace = namespace


class TwoFAEvent(Event):

    def __init__(self, token: str, request: Optional[Request] = None):
        self.token = token
        self.request = request


class UserEvent(Event):

    def __init__(
            self, user, request: Optional[Request] = None, **namespace: Any):
        self.user = user
        self.request = request
        self.namespace = namespace


class UserLoggedInEvent(UserEvent):
    pass


class UserRegisteredEvent(UserEvent):
    pass


class ObjectEvent(Event):

    def __init__(self, obj, request: Optional[Request] = None):
        self.obj = obj
        self.request = request


class ObjectCreatedEvent(ObjectEvent):
    pass


class ObjectAddedEvent(ObjectEvent):
    pass


class ObjectModifiedEvent(ObjectEvent):

    def __init__(self, obj, data, request: Optional[Request] = None):
        self.obj = obj
        self.data = data
        self.request = request


class ObjectRemovedEvent(ObjectEvent):
    pass
