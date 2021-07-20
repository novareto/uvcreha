import horseman.response
from uvcreha.api import routes


@routes.register(
    '/user/{userid:digit}', openapi={'schemas': ['User']}
)
def get_user(request):
    """Get a user
    ---
    get:
      description: Get user info

      responses:
        200:
          description: The user was fetched successfully.
          content:
            application/json:
              schema: {$ref: '#/components/schemas/User'}
        400:
          description: The request content was incorrect.
    """
    return horseman.response.Response(200)


@routes.register(
    '/user/{userid:digit}', methods=['PUT'], openapi={'schemas': ['User']}
)
def create_user(request):
    """Creates a new user
    ---
    put:
      description: creates a new user

      requestBody:
        required: true
        content:
          application/json:
            schema: {$ref: '#/components/schemas/User'}

      responses:
        201:
          description: The user was created successfully.
        400:
          description: The request content was incorrect.
    """
    return horseman.response.Response(200)
