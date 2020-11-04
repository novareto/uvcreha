import horseman.response
from docmanager.app import application
from docmanager.request import Request


@application.route('/users/{username}/folder.add', methods=['POST', 'PUT'])
def folder_add(request: Request, username: str):
    model = request.app.models.user_model(request)
    if not model.exists(request.app.database, username):
        return horseman.response.reply(404)

    model = request.app.models.file_model(request)
    data = request.extract()
    folder = model.create(
        request.app.database, username=username, **data['form'].to_dict())

    return horseman.response.reply(
        200, body=folder.json(by_alias=True),
        headers={'Content-Type': 'application/json'})


@application.route('/users/{username}/folders/{folderid}', methods=['GET'])
def folder_view(request: Request, username: str, folderid: str):
    model = request.app.models.file_model(request)
    folder = model.find_one(
        request.app.database, _key=folderid, username=username)
    if not folder:
        return horseman.response.reply(404)

    return horseman.response.reply(
        200, body=folder.json(by_alias=True),
        headers={'Content-Type': 'application/json'})


@application.route('/users/{username}/folders/{folderid}', methods=['DELETE'])
def folder_delete(request: Request, username: str, folderid: str):
    model = request.app.models.file_model(request)
    folder = model.find_one(
        request.app.database, _key=folderid, username=username)
    if not folder:
        return horseman.response.reply(404)

    model.delete(request.app.database, folderid)
    return horseman.response.reply(202)
