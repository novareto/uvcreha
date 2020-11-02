import horseman.response
from docmanager import db
from docmanager.app import application
from docmanager.request import Request
from roughrider.validation.types import Factory


@application.route(
    '/users/{username}/folder.add',
    methods=['POST', 'PUT'])
def folder_add(request: Request, folder: db.Folder):
    request.database_session.add(db.SQLFolder(**folder.dict()))
    request.database_session.commit()
    return horseman.response.json_reply(201, body={'id': folder.az})


@application.route(
    '/users/{username}/folders/{folderid}',
    methods=['GET'])
def folder_view(request: Request, folder: Factory(db.SQLFolder)):
    model = db.Folder.from_orm(folder)
    return horseman.response.reply(
        200, body=model.json(),
        headers={'Content-Type': 'application/json'})


@application.route(
    '/users/{username}/folders/{folderid}',
    methods=['DELETE'])
def folder_delete(request: Request, username: str, folderid: str):
    session = request.database_session
    session.query(db.SQLFolder).filter(
        db.SQLFolder.username==username, db.SQLFolder.az==folderid).delete()
    session.commit()
    return horseman.response.reply(202)


@application.route(
    '/users/{username}/folders/{folderid}/details',
    methods=['GET'])
def folder_details(request: Request, folder: Factory(db.SQLFolder)):
    model = db.FolderWithDocument.from_orm(folder)
    return horseman.response.reply(
        200, body=model.json(),
        headers={'Content-Type': 'application/json'})
