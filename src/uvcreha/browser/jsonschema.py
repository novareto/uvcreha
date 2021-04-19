from horseman.response import Response, reply
from uvcreha.app import browser
from uvcreha.models import JSONSchemaRegistry


@browser.route("/jsonschema/{schema}", name="jsonschema")
def jsonschema(request, schema: str):
    structure = JSONSchemaRegistry.get(schema)
    if structure is None:
        return reply(404)
    return Response.to_json(body=structure)
