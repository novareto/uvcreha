import logging
import re
from pathlib import Path
from autoroutes import Routes

import horseman.meta
import horseman.response
import roughrider.routing.node
import roughrider.routing.route
import roughrider.validation.dispatch
from roughrider.validation.types import Factory

from docmanager.models import User, Document
from docmanager.db import Database
from docmanager.layout import template_endpoint
from docmanager.request import Request

from .layout import template_endpoint, TEMPLATES, layout
from .utils.openapi import generate_doc


class Application(horseman.meta.SentryNode,
                  roughrider.routing.node.RoutingNode):

    __slots__ = ('config', 'db')
    clean_path_pattern = re.compile(r":[^}]+(?=})")

    def __init__(
            self, routes=None, config=None, db=None, request_factory=Request):
        if routes is None:
            routes = Routes()
        self.routes = routes
        self.config = config
        self.request_factory = request_factory
        self.db = db
        self._middlewares = []
        self._routes_registry = {}

    @property
    def logger(self):
        return logging.getLogger(self.config.logger.name)

    def set_configuration(self, config: dict):
        self.config = config

    def set_database(self, db: Database):
        self.db = db

    def register_middleware(self, middleware, order=0):
        self._middlewares.append((order, middleware))

    def route(self, path: str, methods: list=None, **extras):
        def routing(view):
            for fullpath, method, func in \
                roughrider.routing.route.route_payload(
                    path, view, methods):
                cleaned = self.clean_path_pattern.sub("", fullpath)
                name = extras.pop("name", None)
                if not name:
                    name = view.__name__.lower()
                if name in self._routes_registry:
                    _, handler = self._routes_registry[name]
                    if handler != view:
                        ref = f"{handler.__module__}.{handler.__name__}"
                        raise ValueError(
                            f"Route with name {name} already exists: {ref}.")
                self._routes_registry[name] = cleaned, view
                payload = {
                    method: roughrider.validation.dispatch.Dispatcher(func),
                    **extras
                }
                self.routes.add(fullpath, **payload)
        return routing

    def url_for(self, name: str, **kwargs):
        try:
            path, _ = self._routes_registry[name]
            # Raises a KeyError too if some param misses
            return path.format(**kwargs)
        except KeyError:
            raise ValueError(
                f"No route found with name {name} and params {kwargs}")

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


application = Application()



@application.route('/', methods=['GET'])
@template_endpoint(template=TEMPLATES["index.pt"], layout=layout, raw=False)
def index(request: Request):
    import pdb; pdb.set_trace()
    return dict(request=request)



@application.route('/doc')
@template_endpoint(template=TEMPLATES['swagger.pt'], raw=False)
def doc_swagger(request: Request):
    return {'url': '/openapi.json'}


@application.route('/openapi.json')
def openapi(request: Request):
    open_api = generate_doc(request.app.routes)
    return horseman.response.reply(
        200,
        body=open_api.json(by_alias=True, exclude_none=True, indent=2),
        headers={'Content-Type': 'application/json'}
    )



@application.route('/user.add', methods=['POST', 'PUT'], ns="api")
def add_user(request: Request, user: User):
    users = request.app.db.connector.collection('users')
    data = user.dict()
    data['_key'] = user.username
    metadata = users.insert(data)
    return horseman.response.json_reply(
        201, body={'userid': metadata['_key']})


@application.route('/users/{userid}', methods=['GET'])
def user_view(user: Factory(User)):
    return horseman.response.reply(
        200, body=user.json(),
        headers={'Content-Type': 'application/json'})


@application.route('/users/{userid}/documents', methods=['GET'])
def user_list_docs(request: Request, userid: str):
    ownership = request.app.db.connector.graph('ownership')
    own = ownership.edge_collection('own')
    links = own.edges(f'users/{userid}', direction='out')
    documents = [edge['_to'] for edge in links['edges']]
    return horseman.response.json_reply(200, body=documents)


@application.route('/users/{userid}', methods=['DELETE'])
def user_delete(request: Request, userid: str):
    users = request.app.db.connector.collection('users')
    users.delete(userid)
    return horseman.response.reply(204)


@application.route('/users/{userid}/document.add', methods=['POST', 'PUT'])
def add_document(request: Request, userid: str, document: Document):
    documents = request.app.db.connector.collection('documents')
    metadata = documents.insert(document.dict())
    ownership = request.app.db.connector.graph('ownership')
    own = ownership.edge_collection('own')
    own.insert({
        '_key': f"{userid}-{metadata['_key']}",
        '_from': f"users/{userid}",
        '_to': metadata['_id'],
    })
    return horseman.response.json_reply(
        201, body={'docid': metadata['_key']})
