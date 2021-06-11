import orjson
from typing import Dict, Any
from pathlib import Path
from json_ref_dict.ref_dict import RefDict
from json_ref_dict.loader import get_document


class JSONSchemaStore:
    def __init__(self, *managed_urls):
        self.schemas = {}
        self.urls = set(
            (url + "/" if not url.endswith("/") else url for url in managed_urls)
        )

    def add(self, name: str, schema: dict):
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
                print(f'JSONSchema: loading {f.as_uri()}')
                with f.open('r') as fd:
                    schema = orjson.loads(fd.read())
                    store.add(schema.get('id', f.name), schema)


store: JSONSchemaStore = JSONSchemaStore()
get_document.register(store.fetch)
