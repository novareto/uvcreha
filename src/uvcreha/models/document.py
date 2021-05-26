from uvcreha.workflow import document_workflow
from uvcreha.jsonschema import store
from uvcreha.contenttypes import registry, Content


@registry.factory(
    "document", schema=store.get('Document'), collection="documents")
class Document(Content):

    def set_metadata(self, data):
        wf = document_workflow(data)
        self.id = data['uid']
        self.date = data['creation_date']
        self.title = f"Document {data['az']} ({data['content_type']})"
        self.state = wf.state


@Document.actions.register('default', title="View")
def view(request, item):
    return request.route_path(
        'doc.view', uid=item['uid'], az=item['az'], docid=item['docid'])


@Document.actions.register('edit', title="Bearbeiten", css='fa fa-edit')
def edit(request, item):
    return request.route_path(
        'doc.edit', uid=item['uid'], az=item['az'], docid=item['docid'])
