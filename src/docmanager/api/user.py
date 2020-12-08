import horseman.response
from docmanager.app import api
from docmanager.request import Request
from docmanager.models import User
from reiter.routing.predicates import with_predicates, content_types


@api.route('/user.add', methods=['POST', 'PUT'])
@with_predicates(content_types({'application/json'}))
def user_add(request: Request):
    data = request.extract()
    user = User(**data.json)
    request.database.add(user)
    if user is None:
        return horseman.response.Response.create(400)
    return horseman.response.Response.to_json(
        201, body={'id': user.username})


@api.route('/users/{username}', methods=['GET'])
def user_view(request: Request, username: str):
    model = request.database.bind(User)
    item = model.fetch(username)
    if item is None:
        return horseman.response.Response.create(404)
    return horseman.response.Response.from_json(200, body=item.json())


@api.route('/users/{username}', methods=['DELETE'])
def user_delete(request: Request, username: str):
    model = request.database.bind(User)
    if model.delete(username):
        return horseman.response.Response.create(202)
    return horseman.response.Response.create(404)


@api.route('/users/{username}/files', methods=['GET'])
def user_files(request: Request, username: str):
    model = request.database.bind(User)
    files = "[{}]".format(','.join([
        file.json() for file in model.files(username=username)]))
    return horseman.response.Response.from_json(200, body=files)
