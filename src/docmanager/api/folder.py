import horseman.response
from docmanager.app import api
from docmanager.request import Request
from docmanager.models import File


@api.route('/users/{username}/file.add', methods=['POST', 'PUT'])
def file_add(request: Request, username: str):
    data = request.extract()
    item, _ = request.database(File).create(username=username, **data.json)
    return horseman.response.Response.from_json(201, body=item.json())


@api.route('/users/{username}/files/{fileid}', methods=['GET'])
def file_view(request: Request, username: str, fileid: str):
    if (file := request.database(File).find_one(
            _key=fileid, username=username)) is not None:
        return horseman.response.Response.from_json(200, body=file.json())
    return horseman.response.reply(404)


@api.route('/users/{username}/files/{fileid}', methods=['DELETE'])
def file_delete(request: Request, username: str, fileid: str):
    if (request.database(File).find_one(
            _key=fileid, username=username)) is not None:
        request.database(File).delete(fileid)
        return horseman.response.reply(202)
    return horseman.response.reply(404)


@api.route('/users/{username}/files/{fileid}/docs', methods=['GET'])
def file_documents(request: Request, username: str, fileid: str):
    found = request.database(File).documents(username=username, az=fileid)
    docs = "[{}]".format(','.join([doc.json() for doc in found]))
    return horseman.response.Response.from_json(200, body=docs)
