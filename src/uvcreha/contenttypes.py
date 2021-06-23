import jsonschema_rs
from typing import Optional, Dict, Any

import roughrider.contenttypes
import reiter.arango.meta
from reiter.arango.binding import Binder


class Content(reiter.arango.meta.Content, roughrider.contenttypes.Content):
    """Content class
    """
    def get_action(self, request, name):
        action = self.actions[name]
        return action, action.resolve(request, self)

    def get_actions(self, request):
        default = self.actions.get("default")
        if default is not None:
            yield default, default.resolve(request, self)
        else:
            yield None, None
        for name, action in self.actions.items():
            if name != "default":
                yield action, action.resolve(request, self)


class ContentType(roughrider.contenttypes.ContentType):

    __slots__ = ("factory", "schema", "collection")

    schema: Dict
    collection: Optional[str]

    def __init__(self, factory, schema, collection=None):
        self.factory = factory
        self.schema = schema
        self.collection = collection

    def validate(self, data):
        validator = jsonschema_rs.JSONSchema(self.schema)
        validator.validate(data)  # may raise jsonschema_rs ValidationError

    def bind(self, db: Any, create: bool = True):
        if self.collection is None:
            raise NotImplementedError(
                "You can't bind a content type with no defined collection.")
        return Binder(db=db, content=self, create=create)


class ContentTypesRegistry(roughrider.contenttypes.Registry):

    def new(self,
            name: str,
            schema: Dict, factory: Content, collection: str = None):
        self.register(
            name,
            ContentType(
                schema=schema,
                factory=factory,
                collection=collection
            )
        )

    def factory(self, name: str, schema: Dict, collection: str = ""):
        """Decorator for registering a new content type
        """
        def register_contenttype(cls: Content):
            self.new(name, schema, factory=cls, collection=collection)
            return cls

        return register_contenttype


# Content Types registry singleton
registry = ContentTypesRegistry()

# Exposing for convenience
Action = roughrider.contenttypes.Action  # noqa
