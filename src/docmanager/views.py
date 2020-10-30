import orjson
import horseman.response
from roughrider.validation.types import Factory
from docmanager.app import application
from docmanager.layout import template, TEMPLATES
from docmanager.request import Request
from docmanager import sql


@application.routes.register('/user.add', methods=['POST', 'PUT'], ns="api")
def add_user(request: Request, user: sql.User):
    request.database_session.add(sql.SQLUser(**user.dict()))
    request.database_session.commit()
    return horseman.response.json_reply(201, body={'id': user.username})


@application.routes.register('/users/{userid}', methods=['GET'])
def user_view(user: Factory(sql.SQLUser)):
    model = sql.User.from_orm(user)
    return horseman.response.reply(
        200, body=model.json(),
        headers={'Content-Type': 'application/json'})


@application.routes.register('/users/{userid}/details', methods=['GET'])
def user_details(user: Factory(sql.SQLUser)):
    model = sql.UserWithFolders.from_orm(user)
    return horseman.response.reply(
        200, body=model.json(),
        headers={'Content-Type': 'application/json'})


@application.routes.register('/users/{userid}/folders', methods=['GET'])
def user_folders(request: Request, userid: str):
    folders = request.database_session.query(sql.SQLFolder).filter(
        sql.SQLFolder.username == userid)
    body = orjson.dumps([sql.Folder.from_orm(f).dict() for f in folders])
    return horseman.response.reply(
        200, body=body,
        headers={'Content-Type': 'application/json'})


@application.routes.register('/users/{username}/folder.add', methods=['POST', 'PUT'])
def add_folder(request: Request, folder: sql.Folder):
    request.database_session.add(sql.SQLFolder(**folder.dict()))
    request.database_session.commit()
    return horseman.response.json_reply(201, body={'id': folder.az})
