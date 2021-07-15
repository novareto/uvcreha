import jsonschema_rs
from typing import Optional, Dict, Any, Union, Type
from json_ref_dict import materialize

import roughrider.contenttypes
import reiter.arango.meta
from reiter.arango.binding import Binder
from uvcreha import events
from uvcreha.request import Request


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


class CRUD:

    def __init__(self, app, binding: Binder):
        self.app = app
        self.binding = binding

    def create(self, data: dict, request=None):
        item = self.binding.content.factory.create(data)
        obj, response = self.binding.create(_key=item.id, **data)
        self.app.notify(events.ObjectCreatedEvent(item, request=request))
        return obj

    def update(self, item: Content, data: dict, request=None):
        response = self.binding.update(item.id, **data)
        self.app.notify(
            events.ObjectModifiedEvent(item, data, request=request)
        )
        return response

    def delete(self, item: Content, request=None) -> None:
        self.binding.delete(item.id)
        self.app.notify(events.ObjectRemovedEvent(item, request=request))


class ContentType(roughrider.contenttypes.ContentType):

    factory: Content
    schema: Dict
    collection: Optional[str]
    crud: Optional[Type[CRUD]]

    def __init__(self, factory, schema, collection=None, crud=CRUD):
        self.factory = factory
        self.schema = schema
        self.collection = collection
        self.crud = crud

    def validate(self, data: Dict):
        validator = jsonschema_rs.JSONSchema(materialize(self.schema))
        validator.validate(data)  # may raise jsonschema_rs ValidationError

    def bind(self, db: Any, create: bool = True):
        if self.collection is None:
            raise NotImplementedError(
                "You can't bind a content type with no defined collection.")
        return Binder(db=db, content=self, create=create)

    def get_crud(self, app) -> Optional[CRUD]:
        db = app.utilities['arango'].get_database()
        if self.crud is not None:
            binding = self.bind(db)
            return self.crud(app, binding)


class ContentTypesRegistry(roughrider.contenttypes.Registry):

    def new(self,
            name: str,
            schema: Dict,
            factory: Content,
            collection: str = None,
            crud: Type[CRUD] = CRUD
    ):
        self.register(
            name,
            ContentType(
                schema=schema,
                factory=factory,
                collection=collection,
                crud=crud
            )
        )

    def factory(self,
                name: str,
                schema: Dict,
                collection: str = "",
                crud: Type[CRUD] = CRUD
    ):
        """Decorator for registering a new content type
        """
        def register_contenttype(cls: Content):
            self.new(
                name, schema, factory=cls, collection=collection, crud=crud
            )
            return cls

        return register_contenttype


# Content Types registry singleton
registry = ContentTypesRegistry()

# Exposing for convenience
Action = roughrider.contenttypes.Action  # noqa
