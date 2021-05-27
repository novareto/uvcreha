import arango
from contextlib import contextmanager
from typing import NamedTuple, List, Optional, Type, Tuple, Iterable
from roughrider.contenttypes import ContentType, Content


@contextmanager
def transaction(db, collection):
    transaction = db.begin_transaction(exclusive=collection)
    try:
        yield transaction
        transaction.commit_transaction()
    except Exception:
        transaction.abort_transaction()
        raise


class Binder:

    __slots__ = ('db', 'content_type')

    db: arango.database.StandardDatabase
    content_type: ContentType

    def __init__(self, db, content_type: ContentType):
        self.db = db
        self.content_type = content_type

    def find(self, **filters) -> Iterable[Content]:
        collection = self.db.collection(self.content_type.collection)
        return (
            self.content_type.factory(data)
            for data in collection.find(filters)
        )

    def find_one(self, **filters) -> Optional[Content]:
        collection = self.db.collection(self.content_type.collection)
        found = collection.find(filters, limit=1)
        if not found.count():
            return None
        data = found.next()
        return self.content_type.factory(data)

    def fetch(self, key) -> Optional[Content]:
        collection = self.db.collection(self.content_type.collection)
        if (data := collection.get(key)) is not None:
            return self.content_type.factory(data)

    def create(self, _key=None, **data) -> Tuple[Content, dict]:
        item = self.content_type.factory.create(data)
        try:
            with transaction(self.db, self.content_type.collection) as txn:
                collection = txn.collection(self.content_type.collection)
                if _key is not None:
                    response = collection.insert(
                        {**item.data, '_key': _key})
                else:
                    response = collection.insert(item.data)
                item.data.update(response)
                return item, response
        except arango.exceptions.DocumentInsertError as exc:
            raise horseman.http.HTTPError(exc.http_code, exc.message)

    def exists(self, key) -> bool:
        collection = self.db.collection(self.content_type.collection)
        return collection.has({"_key": key})

    def delete(self, key) -> bool:
        try:
            with transaction(self.db, self.content_type.collection) as txn:
                collection = txn.collection(self.content_type.collection)
                collection.delete(key)
        except arango.exceptions.DocumentDeleteError as exc:
            raise horseman.http.HTTPError(exc.http_code, exc.message)

    def update(self, _key, **data) -> str:
        try:
            with transaction(self.db, self.content_type.collection) as txn:
                collection = txn.collection(self.content_type.collection)
                data = {'_key': _key, **data}
                response = collection.update(data)
                return response
        except arango.exceptions.DocumentUpdateError as exc:
            raise horseman.http.HTTPError(exc.http_code, exc.message)

    def replace(self, _key, **data) -> str:
        try:
            with transaction(self.db, self.content_type.collection) as txn:
                collection = txn.collection(self.content_type.collection)
                data = {'_key': _key, **data}
                response = collection.replace(data)
                return response
        except arango.exceptions.DocumentUpdateError as exc:
            raise horseman.http.HTTPError(exc.http_code, exc.message)

    def create_collection(self):
        self.db.create_collection(self.content_type.collection)

    @property
    def collection_exists(self):
        return self.db.has_collection(self.content_type.collection)
