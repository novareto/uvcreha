import jsonschema_rs
import roughrider.contenttypes
from typing import Optional, Dict, Any
from roughrider.contenttypes import Action
from uvcreha.binder import Binder


class Content(roughrider.contenttypes.Content):

    def get_actions(self, request):
        default = self.actions.get('default')
        if default is not None:
            yield default, default.resolve(request, self)
        else:
            yield None, None
        for name, action in self.actions.items():
            if name != 'default':
                yield action, action.resolve(request, self)


class ContentType(roughrider.contenttypes.ContentType):

    __slots__ = ('factory', 'schema', 'collection')

    schema: Dict
    collection: Optional[str]

    def __init__(self, factory, schema, collection=None):
        self.factory = factory
        self.schema = schema
        self.collection = collection

    def validate(self, data):
        validator = jsonschema_rs.JSONSchema(self.schema)
        validator.validate(data)  # may raise jsonschema_rs ValidationError

    def bind(self, db: Any):
        return Binder(db=db, content_type=self)


class ContentTypesRegistry(roughrider.contenttypes.Registry):

    def new(self,
            name: str,
            schema: Dict,
            factory: Content,
            collection: str = None
    ):
        self.register(
            name, ContentType(
                schema=schema, factory=factory, collection=collection))

    def factory(self, name: str, schema: Dict, collection: str = ''):
        def register_contenttype(cls: Content):
            self.register(
                name, ContentType(
                    schema=schema, factory=cls, collection=collection))
            return cls
        return register_contenttype


registry = ContentTypesRegistry()

Action  # noqa
