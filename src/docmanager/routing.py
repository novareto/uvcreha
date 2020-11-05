import re
from http import HTTPStatus

import autoroutes
import dataclasses
import roughrider.routing.route
from horseman.http import HTTPError


@dataclasses.dataclass
class Route:
    path: str
    method: str
    endpoint: callable
    params: dict = dataclasses.field(default_factory=dict)
    extras: dict = dataclasses.field(default_factory=dict)


class Routes(autoroutes.Routes):

    __slots__ = ('_registry')

    clean_path_pattern = re.compile(r":[^}]+(?=})")

    def __init__(self, *args):
        super().__init__(*args)
        self._registry = {}

    def url_for(self, name: str, **kwargs):
        try:
            path, _ = self._registry[name]
            # Raises a KeyError too if some param misses
            return path.format(**kwargs)
        except KeyError:
            raise ValueError(
                f"No route found with name {name} and params {kwargs}")

    def register(self, path: str, methods: list=None, **extras):
        def routing(view):
            for fullpath, method, func in \
                roughrider.routing.route.route_payload(
                    path, view, methods):
                cleaned = self.clean_path_pattern.sub("", fullpath)
                name = extras.pop("name", None)
                if not name:
                    name = view.__name__.lower()
                if name in self._registry:
                    _, handler = self._registry[name]
                    if handler != view:
                        ref = f"{handler.__module__}.{handler.__name__}"
                        raise ValueError(
                            f"Route with name {name} already exists: {ref}.")
                self._registry[name] = cleaned, view
                payload = {
                    method: func,
                    'extras': extras
                }
                self.add(fullpath, **payload)
        return routing

    def match(self, method: str, path_info: str) -> Route:
        methods, params = super().match(path_info)
        if methods is None:
            return None
        endpoint = methods.get(method)
        if endpoint is None:
            raise HTTPError(HTTPStatus.METHOD_NOT_ALLOWED)

        return Route(
            path=path_info,
            method=method,
            endpoint=endpoint,
            params=params,
            extras=methods.get('extras', {})
        )
