import horseman.response
from docmanager.app import application
from docmanager.request import Request


@application.route(
    '/users/{username}/folder.add',
    methods=['POST', 'PUT'])
def folder_add(request: Request):
    model = request.app.models.get('user')
    user = model.fetch(request.app.database, request.route.params['username'])
    if user is None:
        return horseman.response.reply(404)

    data = request.extract()
    model = request.app.models.get('file')
    folder = model(**data['form'].dict())
    user.files[folder.key] = folder
    user.update(request.app.database)
    return horseman.response.reply(
        200, body=folder.json(),
        headers={'Content-Type': 'application/json'})


@application.route(
    '/users/{username}/folders/{folderid}',
    methods=['GET'])
def folder_view(request: Request):
    model = request.app.models.get('user')
    user = model.fetch(request.app.database, request.route.params['username'])
    if user is None:
        return horseman.response.reply(404)

    folder = user.files[request.route.params['folderid']]
    return horseman.response.reply(
        200, body=folder.json(),
        headers={'Content-Type': 'application/json'})


@application.route(
    '/users/{username}/folders/{folderid}',
    methods=['DELETE'])
def folder_delete(request: Request):
    model = request.app.models.get('user')
    user = model.fetch(request.app.database, request.route.params['username'])
    if user is None:
        return horseman.response.reply(404)

    del user.files[request.route.params['folderid']]
    import pdb
    pdb.set_trace()
    user.update(request.app.database)
    return horseman.response.reply(202)
