import re
import typing as t
from uvcreha.jsonschema import store
from json_ref_dict.materialize import materialize
from apispec import APISpec, BasePlugin
from apispec.yaml_utils import load_operations_from_docstring
from roughrider.routing.route import Routes, RouteEndpoint, HTTPMethods


class AutoroutesPlugin(BasePlugin):

    SLUGS = re.compile('{(.*?)(:.+)?}')
    NO_TYPING = r'{(.+):.+}'
    MATCHING = {
        ':digit': 'integer',
        ':alpha': 'string'
    }

    def init_spec(self, spec):
        super().init_spec(spec)
        self.spec = spec

    def path_helper(self, path, operations, parameters, **kwargs) -> str:
        """Adds URL parameters based on the path {slugs}
        """
        slugs = self.SLUGS.findall(path)
        for name, typed in slugs:
            parameters.append({
                "name": name,
                "in": "path",
                "required": True,
                "schema": {
                    "type": self.MATCHING.get(typed, 'string')
                }
            })
        return re.sub(self.NO_TYPING, r'{\1}', path)


class APIRoutes(Routes):

    _spec = None

    @property
    def spec(self):
        if self._spec is not None:
            return self._spec

        spec = APISpec(
            title="UVCReha API",
            version="0.1",
            openapi_version="3.0.3",
            plugins=[AutoroutesPlugin()],
        )

        for route in self:
            operations = {}
            for verb, route_endpoint in route.payload.items():
                openapi = route_endpoint.metadata.get('openapi', {})
                if openapi is False:
                    continue

                if isinstance(openapi, t.Mapping):
                    schemas = openapi.get('schemas', None)
                    for name in schemas:
                        if not name in spec.components.schemas:
                            schema = materialize(store.get(name))
                            spec.components.schema(name, schema)

                ops = load_operations_from_docstring(
                    route_endpoint.endpoint.__doc__
                )
                if ops:
                    operations.update(ops)
            if operations:
                spec.path(path=route.path, operations=operations)
        self._spec = spec
        return self._spec

    def add(self, *args, **kwargs):
        if self._spec is not None:
            self._spec = None  # mark as dirty
        super().add(*args, **kwargs)


routes = APIRoutes()
