import horseman.response
from docmanager.app import application
from docmanager.request import Request
from docmanager.db import File


@application.route('/users/{username}/file.add', methods=['POST', 'PUT'])
def file_add(request: Request, username: str):
    data = request.extract()
    model = File(request.db_session)
    file = model.create(username=username, **data['form'].dict())
    return horseman.response.Response.from_json(201, body=file.json())


@application.route('/users/{username}/files/{fileid}', methods=['GET'])
def file_view(request: Request, username: str, fileid: str):
    model = File(request.db_session)
    file = model.find_one(_key=fileid, username=username)
    if file is None:
        return horseman.response.reply(404)
    return horseman.response.Response.from_json(200, body=file.json())


@application.route('/users/{username}/files/{fileid}', methods=['DELETE'])
def file_delete(request: Request, username: str, fileid: str):
    model = File(request.db_session)
    file = model.find_one(_key=fileid, username=username)
    if file is None:
        return horseman.response.reply(404)

    model.delete(fileid)
    return horseman.response.reply(202)
