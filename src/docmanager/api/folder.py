import horseman.response
from docmanager.app import api
from docmanager.request import Request
from docmanager.models import File
from reiter.routing.predicates import with_predicates, content_types


@api.route('/users/{username}/file.add', methods=['POST', 'PUT'])
@with_predicates(content_types({'application/json'}))
def file_add(request: Request, username: str):
    data = request.extract()
    folder = File(
        username=username,
        **data.json
    )
    request.database.add(folder)
    return horseman.response.Response.from_json(201, body=file.json())


@api.route('/users/{username}/files/{fileid}', methods=['GET'])
def file_view(request: Request, username: str, fileid: str):
    model = File(request.db_session)
    file = model.find_one(_key=fileid, username=username)
    if file is None:
        return horseman.response.reply(404)
    return horseman.response.Response.from_json(200, body=file.json())


@api.route('/users/{username}/files/{fileid}', methods=['DELETE'])
def file_delete(request: Request, username: str, fileid: str):
    model = File(request.db_session)
    file = model.find_one(_key=fileid, username=username)
    if file is None:
        return horseman.response.reply(404)

    model.delete(fileid)
    return horseman.response.reply(202)


@api.route('/users/{username}/files/{fileid}/docs', methods=['GET'])
def file_documents(request: Request, username: str, fileid: str):
    docs = "[{}]".format(','.join([
        doc.json() for doc in
        File(request.db_session).documents(
            username=username, az=fileid)]))
    return horseman.response.Response.from_json(200, body=docs)
