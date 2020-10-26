import logging
import re
import reg
from collections import namedtuple
from dataclasses import dataclass, field
from http import HTTPStatus
from pathlib import Path
from pkg_resources import iter_entry_points

from pydantic import BaseModel

import horseman.meta
import horseman.response
from horseman.http import HTTPError

import roughrider.routing.route
import roughrider.validation.dispatch
from roughrider.validation.types import Factory

from docmanager.security import SecurityError
from docmanager.routing import Routes
from docmanager.models import ModelsRegistry, User, Document, File
from docmanager.db import Database
from docmanager.layout import template_endpoint, TEMPLATES, layout
from docmanager.request import Request
from docmanager.utils.openapi import generate_doc


class Application(dict, horseman.meta.SentryNode, horseman.meta.APINode):

    __slots__ = ('config', 'db')

    def __init__(self, config=None, db=None, request_factory=Request):
        self.routes = Routes()
        self.config = config
        self.request_factory = request_factory
        self.db = db
        self._middlewares = []
        self._models_registry= ModelsRegistry()

    @property
    def logger(self):
        return logging.getLogger(self.config.logger.name)

    def set_configuration(self, config: dict):
        self.config = config

    def set_database(self, db: Database):
        self.db = db

    def check_permissions(self, route, environ):
        if permissions := route.extras.get('permissions'):
            user = environ.get(self.config.env.principal)
            if user is None:
                raise SecurityError(None, permissions)
            if not permissions.issubset(user.permissions):
                raise SecurityError(user, permissions - user.permissions)

    def resolve(self, path_info, environ):
        try:
            route = self.routes.match(
                environ['REQUEST_METHOD'], path_info)
            if route is None:
                return None
            environ['horseman.path.params'] = route.params
            self.check_permissions(route, environ)
            request = self.request_factory(self, environ, route)
            return route.endpoint(request)
        except LookupError:
            raise HTTPError(HTTPStatus.METHOD_NOT_ALLOWED)
        except SecurityError as error:
            if error.principal is None:
                raise HTTPError(HTTPStatus.UNAUTHORIZED)
            raise HTTPError(HTTPStatus.FORBIDDEN)

    def register_middleware(self, middleware, order=0):
        self._middlewares.append((order, middleware))

    def middlewares(self):
        def ordered(e):
            return -e[0], repr(e[1])
        yield from (m[1] for m in sorted(self._middlewares, key=ordered))

    def handle_exception(self, exc_info, environ):
        exc_type, exc, traceback = exc_info
        self.logger.debug(exc)

    def __call__(self, environ, start_response):
        caller = super().__call__
        for middleware in self.middlewares():
            caller = middleware(caller)
        return caller(environ, start_response)

    def register_type(self, name):
        def add_type(content_type):
            return self._models_registry.register(name, content_type)
        return add_type


application = Application()


@application.routes.register('/', methods=['GET'], permissions={'document.view'})
@template_endpoint(template=TEMPLATES["index.pt"], layout=layout, raw=False)
def index(request: Request):
    event_klass = request.app._models_registry.get('event')
    obj = event_klass(name="hans", subject="klaus", state="send")
    request.app.db.add_document('cklinger', obj.dict())
    return dict(request=request)


@application.routes.register('/doc')
@template_endpoint(template=TEMPLATES['swagger.pt'], raw=False)
def doc_swagger(request: Request):
    return {'url': '/openapi.json'}


@application.routes.register('/openapi.json')
def openapi(request: Request):
    open_api = generate_doc(request.app.routes)
    return horseman.response.reply(
        200,
        body=open_api.json(by_alias=True, exclude_none=True, indent=2),
        headers={'Content-Type': 'application/json'}
    )


@application.routes.register('/user.add', methods=['POST', 'PUT'], ns="api")
def add_user(request: Request, user: User):
    users = request.app.db.connector.collection('users')
    data = user.dict()
    data['_key'] = user.username
    metadata = users.insert(data)
    return horseman.response.json_reply(
        201, body={'userid': metadata['_key']})


@application.routes.register('/users/{userid}', methods=['GET'])
def user_view(user: Factory(User)):
    return horseman.response.reply(
        200, body=user.json(),
        headers={'Content-Type': 'application/json'})


@application.routes.register('/users/{userid}/documents', methods=['GET'])
def user_list_docs(request: Request, userid: str):
    ownership = request.app.db.connector.graph('ownership')
    own = ownership.edge_collection('own')
    links = own.edges(f'users/{userid}', direction='out')
    documents = [edge['_to'] for edge in links['edges']]
    return horseman.response.json_reply(200, body=documents)


@application.routes.register('/users/{userid}', methods=['DELETE'])
def user_delete(request: Request, userid: str):
    users = request.app.db.connector.collection('users')
    users.delete(userid)
    return horseman.response.reply(204)

@application.routes.register(
    '/users/{userid}/file.add',
    methods=['POST', 'PUT']
)
def add_file(request: Request, userid: str, file: File):
    key = request.app.db.add_file(userid, file.dict())
    return horseman.response.json_reply(
        201, body={'docid': key})

@application.routes.register(
    '/users/{userid}/{file_id}/document.add',
    methods=['POST', 'PUT']
)
def add_document(request: Request, userid: str, file_id:str, document: Document):
    import pdb; pdb.set_trace()
    key = request.app.db.add_document(userid, file_id, document.dict())
    return horseman.response.json_reply(
        201, body={'docid': key})
