import horseman.response
from uvcreha.app import api
from uvcreha.request import Request
from uvcreha.models import User, File


@api.route('/user.add', methods=['POST', 'PUT'], model=User)
def user_add(request: Request):
    data = request.extract()
    user, response = request.database(User).create(**data.json)
    return horseman.response.Response.to_json(
        201, body={'id': user.uid})


@api.route('/users/{uid}', methods=['GET', ], model=User)
def user_view(request: Request, uid: str):
    if (item := request.database(User).fetch(uid)) is not None:
        return horseman.response.Response.from_json(200, body=item.json())
    return horseman.response.Response.create(404)


#  @api.route('/users/{uid}', methods=['DELETE'])
def user_delete(request: Request, uid: str):
    if request.database(User).delete(uid):
        return horseman.response.Response.create(202)
    return horseman.response.Response.create(404)


@api.route('/users/{uid}/files', methods=['GET'])
def user_files(request: Request, uid: str):
    found = request.database(File).find(uid=uid)
    files = "[{}]".format(','.join((file.json() for file in found)))
    return horseman.response.Response.from_json(200, body=files)
