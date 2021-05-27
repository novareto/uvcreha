from uvcreha.workflow import document_workflow
from uvcreha.jsonschema import store
from uvcreha.contenttypes import registry, Content


@registry.factory(
    "document", schema=store.get('Document'), collection="documents")
class Document(Content):

    @property
    def id(self):
        return self['docid']

    @property
    def date(self):
        return self['creation_date']

    @property
    def title(self):
        return f"Document {self.docid} ({self['content_type']})"

    @property
    def state(self):
        wf = document_workflow(self)
        return wf.state


@Document.actions.register('default', title="View")
def view(request, item):
    return request.route_path(
        'doc.view', uid=item['uid'], az=item['az'], docid=item['docid'])


@Document.actions.register('edit', title="Bearbeiten", css='fa fa-edit')
def edit(request, item):
    return request.route_path(
        'doc.edit', uid=item['uid'], az=item['az'], docid=item['docid'])
