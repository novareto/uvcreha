from typing import List
from uvcreha.auth import Filter
from horseman.response import Response
from roughrider.workflow import WorkflowState


def security_bypass(urls: List[str]) -> Filter:
    unprotected = frozenset(urls)

    def _filter(environ, caller, user):
        if environ["PATH_INFO"] in unprotected:
            return caller
        return None  # Continue the chain

    return _filter


def secured(path: str) -> Filter:
    def _filter(environ, caller, user):
        if user is None:
            return Response.redirect(environ["SCRIPT_NAME"] + path)
        return None  # Continue the chain

    return _filter


def filter_user_state(states: List[WorkflowState]) -> Filter:
    forbidden_states = frozenset(states)

    def _filter(environ, caller, user):
        if user.state in forbidden_states:
            return Response(403)
        return None  # Continue the chain

    return _filter


def user_register(state: WorkflowState, path: str) -> Filter:
    def _filter(environ, caller, user):
        if environ["PATH_INFO"] == path:
            return caller
        if user.state is state:
            return Response.redirect(environ["SCRIPT_NAME"] + path)
        return None  # Continue the chain

    return _filter


def TwoFA(path: str) -> Filter:
    def _filter(environ, caller, user):
        if environ["PATH_INFO"] == path:
            return caller
        if not caller.utilities["twoFA"].check_twoFA(environ):
            return Response.redirect(environ["SCRIPT_NAME"] + path)
        return None  # Continue the chain

    return _filter
