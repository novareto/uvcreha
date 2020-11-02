import horseman.response
from docmanager.app import application
from docmanager.request import Request


@application.route(
    '/users/{username}/folder.add',
    methods=['POST', 'PUT'])
def folder_add(request: Request):
    return horseman.response.json_reply(201, body={'id': folder.az})


@application.route(
    '/users/{username}/folders/{folderid}',
    methods=['GET'])
def folder_view(request: Request):
    return horseman.response.reply(
        200, body=model.json(),
        headers={'Content-Type': 'application/json'})


@application.route(
    '/users/{username}/folders/{folderid}',
    methods=['DELETE'])
def folder_delete(request: Request):
    return horseman.response.reply(202)


@application.route(
    '/users/{username}/folders/{folderid}/details',
    methods=['GET'])
def folder_details(request: Request):
    return horseman.response.reply(
        200, body=model.json(),
        headers={'Content-Type': 'application/json'})
