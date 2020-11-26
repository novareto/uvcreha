import horseman.response
from docmanager.app import api
from docmanager.request import Request
from docmanager.db import User


@api.route('/user.add', methods=['POST', 'PUT'])
def user_add(request: Request):
    data = request.extract()
    model = User(request.db_session)
    user = model.create(**data['form'].dict())
    if user is None:
        return horseman.response.Response.create(400)
    return horseman.response.Response.to_json(
        201, body={'id': user.username})


@api.route('/users/{username}', methods=['GET'])
def user_view(request: Request, username: str):
    model = User(request.db_session)
    import pdb; pdb.set_trace()
    item = model.fetch(username)
    if item is None:
        return horseman.response.Response.create(404)
    return horseman.response.Response.from_json(200, body=item.json())


@api.route('/users/{username}', methods=['DELETE'])
def user_delete(request: Request, username: str):
    model = User(request.db_session)
    if model.delete(username):
        return horseman.response.Response.create(202)
    return horseman.response.Response.create(404)


@api.route('/users/{username}/files', methods=['GET'])
def user_files(request: Request, username: str):
    files = "[{}]".format(','.join([
        file.json() for file in
        User(request.db_session).files(username=username)]))
    return horseman.response.Response.from_json(200, body=files)
