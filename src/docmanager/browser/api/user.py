import horseman.response
from docmanager.app import application
from docmanager.browser import Namespace as NS
from docmanager.request import Request
from docmanager.validation import catch_pydantic_exception


@application.route('/user.add', methods=['POST', 'PUT'], ns=NS.API)
@catch_pydantic_exception
def user_add(request: Request):
    data = request.extract()
    model = request.app.models.user_model(request)
    user = model.create(
        database=request.app.database, **data['form'].dict())
    if user is None:
        return horseman.response.Response.create(400)
    return horseman.response.Response.to_json(
        201, body={'id': user.username})


@application.route('/users/{username}', methods=['GET'])
@catch_pydantic_exception
def user_view(request: Request, username: str):
    model = request.app.models.user_model(request)
    item = model.fetch(request.app.database, username)
    if item is None:
        return horseman.response.Response.create(404)
    return horseman.response.Response.from_json(200, body=item.json())


@application.route('/users/{username}', methods=['DELETE'])
@catch_pydantic_exception
def user_delete(request: Request, username: str):
    model = request.app.models.user_model(request)
    if model.delete(request.app.database, username):
        return horseman.response.Response.create(202)
    return horseman.response.Response.create(404)
