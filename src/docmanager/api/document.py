import horseman.response
from docmanager.app import api
from docmanager.request import Request
from docmanager.db import Document


@api.route(
    '/users/{username}/files/{fileid}/doc.add',
    methods=['POST', 'PUT'])
def doc_add(request: Request, username: str, fileid: str):
    data = request.extract()
    form = data['form'].dict()
    model = Document(request.db_session)
    document = model.create(username=username, az=fileid, **form)
    return horseman.response.Response.from_json(201, body=document.json())


@api.route(
    '/users/{username}/files/{fileid}/docs/{docid}',
    methods=['GET'])
def doc_view(request: Request, username: str, fileid: str, docid: str):
    model = Document(request.db_session)
    document = model.find_one(_key=docid, az=fileid, username=username)
    if document is None:
        return horseman.response.reply(404)
    return horseman.response.Response.from_json(200, body=document.json())


@api.route(
    '/users/{username}/files/{fileid}/docs/{docid}',
    methods=['DELETE'])
def doc_delete(request: Request, username: str, fileid: str, docid: str):
    model = Document(request.db_session)
    if model.find_one(_key=docid, az=fileid, username=username) is None:
        return horseman.response.reply(404)
    model.delete(docid)
    return horseman.response.reply(202)
