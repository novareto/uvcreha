import horseman.response
from docmanager.app import application
from docmanager.request import Request


@application.route(
    '/users/{username}/folders/{folderid}/doc.add',
    methods=['POST', 'PUT'])
def doc_add(request: Request):
    return horseman.response.json_reply(201, body={'id': inserted.docid})


@application.route(
    '/users/{username}/folders/{folderid}/docs/{docid}',
    methods=['GET'])
def doc_view(request: Request):
    return horseman.response.reply(
        200, body=model.json(),
        headers={'Content-Type': 'application/json'})


@application.route(
    '/users/{username}/folders/{folderid}/docs/{docid}',
    methods=['DELETE'])
def doc_delete(request: Request, userid: str, docid: str):
    return horseman.response.reply(202)
