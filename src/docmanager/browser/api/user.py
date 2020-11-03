import horseman.response
from docmanager.app import application
from docmanager.request import Request
from docmanager.browser import Namespace as NS


@application.route('/user.add', methods=['POST', 'PUT'], ns=NS.API)
def user_add(request: Request):
    data = request.extract()
    model = request.app.models.get('user')
    user = model.create(request.app.database, data['form'].dict())
    if user is None:
        return horseman.response.reply(400)
    return horseman.response.json_reply(201, body={'id': user.username})


@application.route('/users/{username}', methods=['GET'])
def user_view(request: Request):
    username = request.route.params['username']
    model = request.app.models.get('user')
    item = model.fetch(request.app.database, username)
    if item is None:
        return horseman.response.reply(404)
    return horseman.response.reply(
        200, body=item.json(),
        headers={'Content-Type': 'application/json'})


@application.route('/users/{username}', methods=['DELETE'])
def user_delete(request: Request):
    username = request.route.params['username']
    model = request.app.models.get('user')
    if model.delete(request.app.database, username):
        return horseman.response.reply(202)
    return horseman.response.reply(404)
