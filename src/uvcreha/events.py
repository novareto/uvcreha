from reiter.events.meta import Event


class ObjectEvent(Event):

    def __init__(self, request, obj):
        self.request = request
        self.obj = obj


class ObjectCreatedEvent(ObjectEvent):
    pass


class ObjectAddedEvent(ObjectEvent):
    pass


class ObjectModifiedEvent(ObjectEvent):
    pass


class ObjectRemovedEvent(ObjectEvent):
    pass


class UserEvent(Event):

    def __init__(self, request, user, **namespace):
        self.request = request
        self.user = user
        self.namespace = namespace


class UserLoggedInEvent(UserEvent):
    pass


class UserRegisteredEvent(UserEvent):
    pass


class WorkflowTransitionEvent(Event):

    def __init__(self, transition, obj, **namespace):
        self.transition = transition
        self.obj = obj
        self.namespace = namespace



class TwoFAEvent(Event):

    def __init__(self, request, token):
        self.request = request
        self.token = token
