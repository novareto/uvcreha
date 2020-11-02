import horseman.response
from docmanager import db
from docmanager.app import application
from docmanager.request import Request
from roughrider.validation.types import Factory


@application.route(
    '/users/{username}/folders/{folderid}/doc.add',
    methods=['POST', 'PUT'])
def doc_add(request: Request, folder: Factory(db.SQLFolder), doc: db.Document):
    session = request.database_session
    inserted = db.SQLDocument(**doc.dict())
    db.SQLFolder.documents.append(inserted)
    session.commit()
    session.flush()
    return horseman.response.json_reply(201, body={'id': inserted.docid})


@application.route(
    '/users/{username}/folders/{folderid}/docs/{docid}',
    methods=['GET'])
def doc_view(request: Request, doc: Factory(db.SQLDocument)):
    model = db.Document.from_orm(doc)
    return horseman.response.reply(
        200, body=model.json(),
        headers={'Content-Type': 'application/json'})


@application.route(
    '/users/{username}/folders/{folderid}/docs/{docid}',
    methods=['DELETE'])
def doc_delete(request: Request, userid: str, docid: str):
    session = request.database_session
    session.query(db.SQLDocument).filter(
        db.SQLDocument.folderid==folderid,
        db.SQLDocument.id==docid).delete()
    session.commit()
    return horseman.response.reply(202)
