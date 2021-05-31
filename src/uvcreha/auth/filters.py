from typing import Set
from uvcreha.auth import Filter
from horseman.response import Response
from roughrider.workflow import WorkflowState


def security_bypass(unprotected: Set[str]) -> Filter:
    def _filter(environ, caller, user):
        if environ['PATH_INFO'] in unprotected:
            return caller
        return None  # Continue the chain
    return _filter


def secured(path: str) -> Filter:
    def _filter(environ, caller, user):
        if user is None:
            return Response.redirect(path)
        return None  # Continue the chain
    return _filter


def filter_user_state(forbidden_states: Set[WorkflowState]) -> Filter:
    def _filter(environ, caller, user):
        if user.state in forbidden_states:
            return Response.create(403)
        return None  # Continue the chain
    return _filter


def user_register(state: WorkflowState, url: str) -> Filter:
    def _filter(environ, caller, user):
        if user.state == state:
            return Response.redirect(url)
        return None  # Continue the chain
    return _filter


def TwoFA(path: str) -> Filter:
    def _filter(environ, caller, user):
        if environ['PATH_INFO'] == path:
            return caller
        if not environ['app'].utilities['twoFA'].check_twoFA(environ):
            return Response.redirect(path)
        return None  # Continue the chain
    return _filter
