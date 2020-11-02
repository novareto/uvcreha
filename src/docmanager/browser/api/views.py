import orjson
import horseman.response
from roughrider.validation.types import Factory
from docmanager.app import application
from docmanager.layout import template, TEMPLATES
from docmanager.request import Request
from docmanager import db
from docmanager.browser import Namespace as NS


@application.route('/user.add', methods=['POST', 'PUT'], ns=NS.API)
def add_user(request: Request, user: db.User):
    request.database_session.add(db.SQLUser(**user.dict()))
    request.database_session.commit()
    return horseman.response.json_reply(201, body={'id': user.username})


@application.route('/users/{userid}', methods=['GET'])
def user_view(user: Factory(db.SQLUser)):
    model = db.User.from_orm(user)
    return horseman.response.reply(
        200, body=model.json(),
        headers={'Content-Type': 'application/json'})


@application.route('/users/{userid}/details', methods=['GET'])
def user_details(user: Factory(db.SQLUser)):
    model = db.UserWithFolders.from_orm(user)
    return horseman.response.reply(
        200, body=model.json(),
        headers={'Content-Type': 'application/json'})


@application.route('/users/{userid}/folders', methods=['GET'])
def user_folders(request: Request, userid: str):
    folders = request.database_session.query(db.SQLFolder).filter(
        db.SQLFolder.username == userid)
    body = orjson.dumps([db.Folder.from_orm(f).dict() for f in folders])
    return horseman.response.reply(
        200, body=body,
        headers={'Content-Type': 'application/json'})


@application.route('/users/{username}/folder.add', methods=['POST', 'PUT'])
def add_folder(request: Request, folder: db.Folder):
    request.database_session.add(db.SQLFolder(**folder.dict()))
    request.database_session.commit()
    return horseman.response.json_reply(201, body={'id': folder.az})
