from horseman.response import Response, reply
from uvcreha.app import browser
from uvcreha.jsonschema import store
from functools import wraps
from typing import Iterable
from horseman.http import HTTPCode


def allow_origins(origins: str, codes: Iterable[HTTPCode] = None):
    def cors_wrapper(method):
        @wraps(method)
        def add_cors_header(*args, **kwargs):
            response = method(*args, **kwargs)
            if codes and response.status not in codes:
                return response
            response.headers["Access-Control-Allow-Origin"] = origins
            return response
        return add_cors_header
    return cors_wrapper


@browser.route("/jsonschema/{schema}", name="jsonschema")
@allow_origins("*", [200])
def jsonschema(request, schema: str):
    structure = store.get(schema)
    if structure is None:
        return reply(404)
    return Response.to_json(body=dict(structure))
