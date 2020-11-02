import horseman.response
from docmanager import db
from docmanager.app import application
from docmanager.request import Request


@application.route('/users/{username}/folder.add', methods=['POST', 'PUT'])
def folder_add(request: Request, folder: db.Folder):
    request.database_session.add(db.SQLFolder(**folder.dict()))
    request.database_session.commit()
    return horseman.response.json_reply(201, body={'id': folder.az})


@application.route('/users/{userid}/folders/{folderid}', methods=['GET'])
def folder_view(request: Request, userid: str, folderid: str):
    session = request.database_session
    folder = session.query(db.SQLFolder).filter(
        db.SQLFolder.username==userid, db.SQLFolder.az==folderid).first()
    model = db.Folder.from_orm(folder)
    return horseman.response.reply(
        200, body=model.json(),
        headers={'Content-Type': 'application/json'})


@application.route('/users/{userid}/folders/{folderid}', methods=['DELETE'])
def folder_delete(request: Request, userid: str, folderid: str):
    session = request.database_session
    session.query(db.SQLFolder).filter(
        db.SQLFolder.username==userid, db.SQLFolder.az==folderid).delete()
    session.commit()
    return horseman.response.reply(202)
