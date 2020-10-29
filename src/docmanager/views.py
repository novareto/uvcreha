from roughrider.validation.types import Factory
from docmanager.app import application
from docmanager.layout import template, TEMPLATES
from docmanager.request import Request
from docmanager.models import User, Document, File


@application.routes.register('/', methods=['GET'], permissions={'document.view'})
@template(template=TEMPLATES["index.pt"], layout_name='default', raw=False)
def index(request: Request):
    #event_klass = request.app._models_registry.get('event')
    #obj = event_klass(name="hans", subject="klaus", state="send")
    #request.app.db.add_document('cklinger', obj.dict())
    return dict(request=request)


@application.routes.register('/view', methods=['GET'])
@template(template=TEMPLATES["index.pt"], layout_name='default', raw=False)
def someview(request: Request):
    return {}


@application.routes.register('/doc')
@template(template=TEMPLATES['swagger.pt'], raw=False)
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
    key = request.app.db.add_document(userid, file_id, document.dict())
    return horseman.response.json_reply(
        201, body={'docid': key})
