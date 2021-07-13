import orjson
import logging
from typing import Dict, Any, Optional, NoReturn, NamedTuple
from collections import UserDict
from pathlib import Path
from json_ref_dict.ref_dict import RefDict
from json_ref_dict.loader import get_document


class Version(NamedTuple):
    number: int
    value: Any


class VersionedValue:

    latest: int
    _store: Dict[int, Any]

    def __init__(self):
        self._store = {}
        self.latest = 0

    def get(self, version: Optional[int] = None) -> Version:
        if version is not None:
            version = int(version)
        else:
            version = self.latest
        value = self._store[version]
        return Version(number=version, value=value)

    def __iter__(self):
        for key, value in self._store.items():
            yield Version(number=key, value=value)

    def keys(self):
        return self._store.keys()

    def add(self, value: Any, version: Optional[int] = None) -> int:
        if version is not None:
            version = int(version)  # assert type casting
            assert version > 0, (
                'Version number must be positive and non-null.')
            if version in self._store:
                raise ValueError(f'Version {version} already exists.')
        else:
            version = self.latest + 1

        self._store[version] = value
        if version > self.latest:
            self.latest = version
        return version

    def remove(self, version: int) -> Any:
        version = int(version)
        if version in self._store:
            value = self._store.pop(version)
            keys = self._store.keys()
            if len(keys):
                self.latest = max(keys)
            else:
                self.latest = 0
            return Version(number=version, value=value)
        raise KeyError(f'Unknown version: {version}.')

    def __bool__(self):
        return bool(self._store)

    def __len__(self):
        return len(self._store)


class DocumentItemStore:

    _store: Dict[str, VersionedValue]

    def __init__(self):
        self._store = {}

    def __bool__(self):
        return bool(self._store)

    def __len__(self):
        return len(self._store)

    def __contains__(self, name: str):
        return name in self._store

    def add(self, name: str, item: Any, version: Optional[int] = None) -> int:
        value = self._store.setdefault(name, VersionedValue())
        return value.add(item, version)

    def remove(self, name, version: Optional[int] = None):
        if version is None:
            del self._store[name]
        else:
            self._store[name].remove(version)

    def get(self, name, version: Optional[int] = None) -> Any:
        value = self._store.get(name)
        if value is not None:
            return value.get(version)
        return None

    def versions_for(self, name):
        v = self._store.get(name)
        if v is not None:
            return iter(v.keys())

    def items_for(self, name):
        v = self._store.get(name)
        if v is not None:
            return iter(v)

    def keys(self):
        return self._store.keys()

    def items(self):
        return self._store.items()

    def load_from_folder(self, path: Path):
        for f in path.iterdir():
            if f.suffix == '.json':
                with f.open('r') as fd:
                    schema = orjson.loads(fd.read())
                    key = schema.get('id', f.name)
                    version = schema.pop('$version', None)
                    self.add(key, schema, version=version)
                    logging.info(f'loading {key} : {str(f.absolute())}.')


class JSONSchemaStore:
    def __init__(self, *managed_urls):
        self.schemas = {}
        self.urls = set((
            url + "/" if not url.endswith("/") else url
            for url in managed_urls
        ))

    def add(self, name: str, schema: dict):
        print(name)
        if name in self.schemas:
            raise KeyError(f"Schema {name} already exists.")
        self.schemas[name] = schema

    def items(self):
        return self.schemas.items()

    def remove(self, name: str):
        if name not in self.schemas:
            raise KeyError(f"Schema {name} does not exist.")
        del self.schemas[name]

    def fetch(self, name: str) -> Dict[str, Any]:
        if self.urls:
            for url in self.urls:
                if name.startswith(url):
                    # We manage this url, if the schema is not here,
                    # we should get a hard fail.
                    return self.schemas[name[len(url) :]]

        if name in self.schemas:
            return self.schemas.get(name)
        return ...

    def get(self, name) -> RefDict:
        return RefDict(name)

    def load_from_folder(self, path: Path):
        for f in path.iterdir():
            if f.suffix == '.json':
                with f.open('r') as fd:
                    schema = orjson.loads(fd.read())
                    key = schema.get('id', f.name)
                    self.add(key, schema)
                    logging.info(f'loading {key} : {str(f.absolute())}.')


documents_store: DocumentItemStore = DocumentItemStore()
store: JSONSchemaStore = JSONSchemaStore()
get_document.register(store.fetch)
