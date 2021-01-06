import horseman.response
from docmanager.app import api
from docmanager.request import Request
from docmanager.models import User, File


@api.route('/user.add', methods=['POST', 'PUT'], model=User)
def user_add(request: Request):
    data = request.extract()
    user, response = request.database(User).create(**data.json)
    return horseman.response.Response.to_json(
        201, body={'id': user.username})


@api.route('/users/{username}', methods=['GET', ], model=User)
def user_view(request: Request, username: str):
    if (item := request.database(User).fetch(username)) is not None:
        return horseman.response.Response.from_json(200, body=item.json())
    return horseman.response.Response.create(404)


#@api.route('/users/{username}', methods=['DELETE'])
def user_delete(request: Request, username: str):
    if request.database(User).delete(username):
        return horseman.response.Response.create(202)
    return horseman.response.Response.create(404)


@api.route('/users/{username}/files', methods=['GET'])
def user_files(request: Request, username: str):
    found = request.database(File).find(username=username)
    files = "[{}]".format(','.join((file.json() for file in found)))
    return horseman.response.Response.from_json(200, body=files)
