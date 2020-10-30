import horseman.response
from roughrider.validation.types import Factory
from docmanager.app import application
from docmanager.layout import template, TEMPLATES
from docmanager.request import Request
from docmanager import sql


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


@application.routes.register('/user.add', methods=['POST', 'PUT'], ns="api")
def add_user(request: Request, user: sql.User):
    request.database_session.add(sql.SQLUser(**user.dict()))
    request.database_session.commit()
    return horseman.response.json_reply(
        201, body={'id': user.username})


@application.routes.register('/users/{userid}', methods=['GET'])
def user_view(user: Factory(sql.SQLUser)):
    model = sql.User.from_orm(user)
    return horseman.response.reply(
        200, body=model.json(),
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
    '/users/{userid}/folder.add',
    methods=['POST', 'PUT']
)
def add_folder(request: Request, userid: str, folder: sql.Folder):
    key = request.app.db.add_folder(userid, folder.dict())
    return horseman.response.json_reply(
        201, body={'docid': key})


@application.routes.register(
    '/users/{userid}/{folder_id}/document.add',
    methods=['POST', 'PUT']
)
def add_document(request: Request, userid: str, folder_id: str, document: sql.Document):
    key = request.app.db.add_document(userid, folder_id, document.dict())
    return horseman.response.json_reply(
        201, body={'docid': key})
