import horseman.response
from docmanager.app import api
from docmanager.request import Request
from docmanager.models import Document
from docmanager.workflow import document_workflow


@api.route("/users/{username}/files/{fileid}/doc.add", methods=["POST", "PUT"])
def doc_add(request: Request, username: str, fileid: str):
    data = request.extract()
    model_class = Document.lookup(**data.json)
    import pdb
    pdb.set_trace()
    document = model_class(
        username=username,
        az=fileid,
        **data.json
    )
    request.database.add(document)
    request.app.notify('document_created', user=username, document=document)
    return horseman.response.Response.from_json(201, body=document.json())


@api.route("/users/{username}/files/{fileid}/docs/{docid}", methods=["GET"])
def doc_view(request: Request, username: str, fileid: str, docid: str):
    model = request.database.bind(Document)
    document = model.find_one(_key=docid, az=fileid, username=username)
    if document is None:
        return horseman.response.reply(404)
    return horseman.response.Response.from_json(200, body=document.json())


@api.route("/users/{username}/files/{fileid}/docs/{docid}", methods=["DELETE"])
def doc_delete(request: Request, username: str, fileid: str, docid: str):
    model = request.database.bind(Document)
    if model.find_one(_key=docid, az=fileid, username=username) is None:
        return horseman.response.reply(404)
    model.delete(docid)
    return horseman.response.reply(202)
