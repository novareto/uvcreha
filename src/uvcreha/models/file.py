from uvcreha.workflow import file_workflow
from uvcreha.jsonschema import store
from uvcreha.contenttypes import registry, Content


file_schema = {
    "id": "File",
    "title": "File",
    "type": "object",
    "properties": {
        "uid": {
            "title": "UID",
            "description": "Interne ID des Benutzers",
            "type": "string",
        },
        "az": {
            "title": "Aktenzeichen",
            "description": "Aktenzeichen des entsprechenden Falls",
            "type": "string",
        },
        "mnr": {
            "title": "Mitgliedsnummer",
            "description": "Mitgliedsnummer des Unternehmens",
            "type": "string",
        },
        "vid": {
            "title": "Versichertenfall ID",
            "description": "ID des Versichertenfalls",
            "type": "string",
        },
        "creation_date": {
            "title": "Creation Date",
            "type": "string",
            "format": "date-time",
        },
        "state": {"title": "State", "default": "created", "type": "string"},
        "unternehmen": {"$ref": "Unternehmen#/"},
        "versichertenfall": {"$ref": "VersichertenFall#/"},
    },
    "required": ["uid", "az", "mnr", "vid"],
}


store.add("File", file_schema)


@registry.factory("file", schema=store.get("File"), collection="files")
class File(Content):
    @property
    def id(self):
        return self["az"]

    @property
    def date(self):
        return self["creation_date"]

    @property
    def title(self):
        return f"File {self['az']!r}"

    @property
    def state(self):
        wf = file_workflow(self)
        return wf.state


@File.actions.register("default", title="View")
def view(request, item):
    if request.user.title != "admin":
        if item.state is file_workflow.states.created:
            return request.route_path("file.register", uid=item["uid"], az=item["az"])
    return request.route_path("file.view", uid=item["uid"], az=item["az"])


@File.actions.register("edit", title="Bearbeiten", css="fa fa-edit")
def edit(request, item):
    return request.route_path("file.edit", uid=item["uid"], az=item["az"])


@File.actions.register("doc", title="Dokument anlegen", css="fa fa-file")
def new_doc(request, item):
    return request.route_path("file.new_doc", uid=item["uid"], az=item["az"])
