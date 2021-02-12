import time
import asyncio
import dramatiq
import logging
import horseman.response
from docmanager.app import api
from docmanager.request import Request
from docmanager.models import User, File
from docmanager.tasks import test


async def create(data):
    await asyncio.sleep(2)
    print('Asyncy', data)


@dramatiq.actor(max_age=3000)
def create_task(data):
    time.sleep(2)
    print('Rabbity', data)


@api.route('/user.add', methods=['POST', 'PUT'], model=User)
def user_add(request: Request):
    data = request.extract()
    task = request.app.utilities['tasker'].enqueue(create(data))
    create_task.send(data)
    return horseman.response.Response.to_json(201)


@api.route('/users/{username}', methods=['GET', ], model=User)
def user_view(request: Request, username: str):
    if (item := request.database(User).fetch(username)) is not None:
        return horseman.response.Response.from_json(200, body=item.json())
    return horseman.response.Response.create(404)


#  @api.route('/users/{username}', methods=['DELETE'])
def user_delete(request: Request, username: str):
    if request.database(User).delete(username):
        return horseman.response.Response.create(202)
    return horseman.response.Response.create(404)


@api.route('/users/{username}/files', methods=['GET'])
def user_files(request: Request, username: str):
    found = request.database(File).find(username=username)
    files = "[{}]".format(','.join((file.json() for file in found)))
    return horseman.response.Response.from_json(200, body=files)
