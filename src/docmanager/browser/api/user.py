import horseman.response
from roughrider.validation.types import Factory

from docmanager import db
from docmanager.app import application
from docmanager.request import Request
from docmanager.browser import Namespace as NS


@application.route('/user.add', methods=['POST', 'PUT'], ns=NS.API)
def user_add(request: Request, user: db.User):
    request.database_session.add(db.SQLUser(**user.dict()))
    request.database_session.commit()
    return horseman.response.json_reply(201, body={'id': user.username})


@application.route('/users/{username}', methods=['GET'])
def user_view(user: Factory(db.SQLUser)):
    model = db.User.from_orm(user)
    return horseman.response.reply(
        200, body=model.json(),
        headers={'Content-Type': 'application/json'})


@application.route('/users/{username}', methods=['DELETE'])
def user_delete(request: Request, username: str):
    session = request.database_session
    session.query(db.SQLUser).filter(db.SQLUser.username==username).delete()
    session.commit()
    return horseman.response.reply(202)


@application.route('/users/{username}/details', methods=['GET'])
def user_details(user: Factory(db.SQLUser)):
    model = db.UserWithFolders.from_orm(user)
    return horseman.response.reply(
        200, body=model.json(),
        headers={'Content-Type': 'application/json'})
