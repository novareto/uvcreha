import abc
from uvcreha.request import Request


class SecurityError(Exception):

    def __init__(self, user, *permissions):
        self.permissions = permissions
        self.user = user


class ProtectedModel(abc.ABC):

    __permissions__: list

    @abc.abstractmethod
    def __check_security__(self, request: Request):
        pass
