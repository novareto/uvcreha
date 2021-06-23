import pytest
from uvcreha.request import Request
from uvcreha.contenttypes import Content, ContentType


schema = {
    "id": "Person",
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "title": "Person",
    "type": "object",
    "properties": {
        "name": {
            "type": "string",
            "description": "The person's first name."
        },
        "age": {
            "description": "Age in years, equal to or greater than zero.",
            "type": "integer",
            "minimum": 0,
            "default": 18
        }
    },
    "required": ["name"]
}


class Person(Content):
    name: str
    age: int

    def __init__(self, name, age):
        self.name = name
        self.age = age


def view_person(request, item):
    return request.application_uri() + f'/{item.name}'


def edit_person(request, item):
    return request.application_uri() + f'/{item.name}/edit'


class TestContentType:

    def test_no_collection_validate(self):
        from jsonschema_rs import ValidationError

        ct = ContentType(Person, schema)
        ct.validate({"name": "John"})
        ct.validate({"name": "Jane", "age": 26})

        with pytest.raises(ValidationError):
            ct.validate({"name": "John", "age": "20"})

        with pytest.raises(ValidationError):
            ct.validate({"name": "Jane", "age": -1})

        with pytest.raises(ValidationError):
            ct.validate({"age": "20"})

    def test_no_collection_bind(self, arangodb):
        db = arangodb.get_database()
        ct = ContentType(Person, schema)
        with pytest.raises(NotImplementedError):
            ct.bind(db)

    def test_collection_bind(self, arangodb):
        """We test the creation of the binding, not the binding itself
        This is done in reiter.arango.
        """
        db = arangodb.get_database()
        ct = ContentType(Person, schema, collection='persons')
        binding = ct.bind(db, create=False)
        assert binding.collection_exists is False

        binding = ct.bind(db, create=True)
        assert binding.collection_exists is True


class TestActions:

    def teardown_method(self, test_method):
        Person.actions.clear()

    def test_new_action(self):
        from uvcreha.contenttypes import Action

        assert Person.actions == {}
        Person.actions.register("edit")(edit_person)
        assert Person.actions == {
            'edit': Action(
                name='edit',
                title=None,
                css='',
                resolve=edit_person
            )
        }

        Person.actions.clear()
        assert Person.actions == {}

    def test_action(self, uvcreha, environ):
        from uvcreha.contenttypes import Action

        person = Person(name="Duncan", age=18)
        request = Request(uvcreha, environ, None)

        with pytest.raises(KeyError):
            person.get_action(request, 'edit')

        Person.actions.register("edit")(edit_person)
        assert person.get_action(request, 'edit') == (
            Action(
                name='edit',
                title=None,
                css='',
                resolve=edit_person
            ),
            "http://test_domain.com/Duncan/edit"
        )

    def test_actions(self, uvcreha, environ):
        from uvcreha.contenttypes import Action

        person = Person(name="Duncan", age=18)
        request = Request(uvcreha, environ, None)
        actions = list(person.get_actions(request))
        assert actions == [(None, None)]  # first is always the default

        Person.actions.register("edit")(edit_person)
        actions = list(person.get_actions(request))
        assert actions == [
            (None, None),  # first is always the 'default'
            (Action(
                name='edit',
                title=None,
                css='',
                resolve=edit_person
            ), "http://test_domain.com/Duncan/edit")
        ]

        Person.actions.register("default")(view_person)
        actions = list(person.get_actions(request))
        assert actions == [
            (Action(
                name='default',
                title=None,
                css='',
                resolve=view_person
            ), "http://test_domain.com/Duncan"),
            (Action(
                name='edit',
                title=None,
                css='',
                resolve=edit_person
            ), "http://test_domain.com/Duncan/edit")
        ]
