from uvcreha.workflow import document_workflow
from uvcreha.jsonschema import store
from uvcreha.contenttypes import registry, Content


store.add(
    "Document",
    {
        "id": "Document",
        "title": "Document",
        "type": "object",
        "properties": {
            "docid": {
                "title": "DocumentID",
                "description": "Eindeutige ID des Dokuments",
                "type": "string",
            },
            "az": {
                "title": "Aktenzeichen",
                "description": "Eindeutige ID der Akte",
                "type": "string",
            },
            "uid": {
                "title": "UID Versicherter",
                "description": "Eindeutige ID des Versicherten",
                "type": "string",
            },
            "creation_date": {
                "title": "Creation Date",
                "type": "string",
                "format": "date-time",
            },
            "state": {"title": "State", "type": "string"},
            "content_type": {
                "title": "Dokumentart",
                "description": "Bitte w\u00e4hlen Sie eine Dokumentart",
                "type": "string",
            },
            "item": {
                "title": "Item",
                "type": "object",
                "description": (
                    "Depends on the content_type. Shouldn't be " "exposed in a form."
                ),
            },
        },
        "required": ["docid", "az", "uid"],
    },
)


@registry.factory("document", schema=store.get("Document"), collection="documents")
class Document(Content):
    @property
    def id(self):
        return self["docid"]

    @property
    def date(self):
        return "01.01.2021"
        return self["creation_date"]

    @property
    def title(self):
        return f"Document {self['docid']} ({self['content_type']})"

    @property
    def state(self):
        wf = document_workflow(self)
        return wf.state


@Document.actions.register("default", title="View")
def view(request, item):
    return request.route_path(
        "doc.view", uid=item["uid"], az=item["az"], docid=item["docid"]
    )


@Document.actions.register("edit", title="Bearbeiten", css="fa fa-edit")
def edit(request, item):
    return request.route_path(
        "doc.edit", uid=item["uid"], az=item["az"], docid=item["docid"]
    )
