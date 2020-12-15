import uuid
import horseman.response
from docmanager.app import api
from docmanager.request import Request
from docmanager.models import Document


@api.route("/users/{username}/files/{fileid}/doc.add", methods=["POST", "PUT"])
def doc_add(request: Request, username: str, fileid: str):
    data = request.extract()
    key = str(uuid.uuid4())
    document, response = request.database(Document).create(
        key=key, username=username, az=fileid, **data.json)
    request.app.notify('document_created', user=username, document=document)
    return horseman.response.Response.from_json(201, body=document.json())


@api.route("/users/{username}/files/{fileid}/docs/{docid}", methods=["GET"])
def doc_view(request: Request, username: str, fileid: str, docid: str):
    if (document := request.database(Document).find_one(
            _key=docid, az=fileid, username=username)) is not None:
        return horseman.response.Response.from_json(
            200, body=document.json())

    return horseman.response.reply(404)


@api.route("/users/{username}/files/{fileid}/docs/{docid}", methods=["DELETE"])
def doc_delete(request: Request, username: str, fileid: str, docid: str):
    if (request.database(Document).find_one(
            _key=docid, az=fileid, username=username)) is not None:
        request.database(Document).delete(docid)
        return horseman.response.reply(202)

    return horseman.response.reply(404)
