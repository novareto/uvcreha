from uvcreha.workflow import file_workflow
from uvcreha.jsonschema import store
from uvcreha.contenttypes import registry, Content


@registry.factory("file", schema=store.get('File'), collection="files")
class File(Content):

    @property
    def id(self):
        return self['az']

    @property
    def date(self):
        return self['creation_date']

    @property
    def title(self):
        return f"File {data['az']!r}"

    @property
    def state(self):
        wf = file_workflow(self)
        return wf.state


@File.actions.register('default', title="View")
def view(request, item):
    if item.state is file_workflow.states.created:
        return request.route_path(
            'file.register', uid=item['uid'], az=item['az'])
    return request.route_path(
        'file.view', uid=item['uid'], az=item['az'])


@File.actions.register('edit', title="Bearbeiten", css='fa fa-edit')
def edit(request, item):
    return request.route_path(
        'file.edit', uid=item['uid'], az=item['az'])


@File.actions.register('doc', title="Dokument anlegen", css='fa fa-file')
def new_doc(request, item):
    return request.route_path(
        'file.new_doc', uid=item['uid'], az=item['az'])
