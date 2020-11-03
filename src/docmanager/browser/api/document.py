import horseman.response
from docmanager.app import application
from docmanager.request import Request


@application.route(
    '/users/{username}/folders/{folderid}/doc.add',
    methods=['POST', 'PUT'])
def doc_add(request: Request, username: str, folderid: str):
    model = request.app.models.file_model(request)
    folder = model.find_one(
        request.app.database, _key=folderid, username=username)
    if not folder:
        return horseman.response.reply(404)

    data = request.extract()
    form = data['form'].dict()

    model = request.app.models.document_model(
        request, content_type=form.get('content_type', 'default'))
    document = model.create(
        request.app.database, username=username, az=folderid, **form)

    return horseman.response.reply(
        201, body=document.json(by_alias=True),
        headers={'Content-Type': 'application/json'})

@application.route(
    '/users/{username}/folders/{folderid}/docs/{docid}',
    methods=['GET'])
def doc_view(request: Request, username: str, folderid: str, docid: str):
    model = request.app.models.document_model(request)
    data = model.find_one(
        request.app.database, _key=docid, az=folderid, username=username)
    if not data:
        return horseman.response.reply(404)

    model = request.app.models.document_model(
        request, content_type=data['content_type'])

    document = model(**data)
    return horseman.response.reply(
        200, body=document.json(),
        headers={'Content-Type': 'application/json'})


@application.route(
    '/users/{username}/folders/{folderid}/docs/{docid}',
    methods=['DELETE'])
def doc_delete(request: Request, username: str, folderid: str, docid: str):
    model.delete(request.app.database, folderid)
    document = model.find_one(
        request.app.database, _key=docid, az=folderid, username=username)
    if not document:
        return horseman.response.reply(404)

    model.delete(request.app.database, docid)
    return horseman.response.reply(202)
