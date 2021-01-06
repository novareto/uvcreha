from collections import defaultdict
from openapi_schema_pydantic import (
    Info,
    MediaType,
    OpenAPI,
    Operation,
    PathItem,
    RequestBody,
    Response,
)
from openapi_schema_pydantic.util import (
    PydanticSchema,
    construct_open_api_with_schema_class,
)
from pydantic import create_model


def construct_base_open_api(api: dict) -> OpenAPI:

    paths = {}
    for path, methods in api.items():
        items = {}
        for method, signature in methods.items():
            items[method.lower()] = Operation(
                requestBody=RequestBody(
                    content={
                        "application/json": MediaType(
                            schema=PydanticSchema(schema_class=signature)
                        )
                    }
                ),
                responses={
                    "200": Response(
                        description="pong",
                        content={
                            "application/json": MediaType(
                                schema=PydanticSchema(schema_class=signature)
                            )
                        },
                    )
                },
            )
        paths[path] = PathItem(**items)
    return OpenAPI(
        info=Info(
            title="ADHoc API",
            version="v0.0.1",
        ),
        paths=paths,
    )


def make_api(api: dict, node, level=0):
    if node.payload:
        extras = node.payload.pop('extras', {})
        model = extras.get('model', None)
        if model:
            for method, dispatcher in node.payload.items():
                api["api%s" %node.path][method] = create_model(
                    f"api/{node.path.replace('/', '_')}_{method.lower()}",
                    __base__=model,
                )

    if node.edges:
        for edge in node.edges:
            if edge.child:
                make_api(api, edge.child, level + 1)
    return api


def generate_doc(router):
    api = make_api(defaultdict(dict), router.root)
    print(api)
    open_api = construct_base_open_api(api)
    open_api = construct_open_api_with_schema_class(open_api)
    return open_api
