from horseman.prototyping import Environ
from horseman.response import Response
from docmanager.db import User
from docmanager.workflow import user_workflow


class Auth:

    unprotected = {'/login', '/webpush'}
    forbidden_states = {
        user_workflow.states.inactive,
        user_workflow.states.closed
    }

    def __init__(self, model, config):
        self.model = model
        self.config = config

    def from_credentials(self, credentials: dict):
        return self.model.find_one(
            username=credentials['username'],
            password=credentials['password']
        )

    def identify(self, environ: Environ):
        if (user := environ.get(self.config.user)) is not None:
            return user
        session = environ.get(self.config.session)
        if (user_key := session.get(self.config.user, None)) is not None:
            user = environ[self.config.user] = self.model.fetch(user_key)
            return user
        return None

    def remember(self, environ: Environ, user):
        session = environ.get(self.config.session)
        session[self.config.user] = user.key
        environ[self.config.user] = user

    def __call__(self, app):

        def auth_application_wrapper(environ, start_response):
            user = self.identify(environ)

            if environ['PATH_INFO'] not in self.unprotected:
                # App results need protection checks now.

                if user is None:
                    # Protected access and no user. Go login.
                    return Response.create(
                        302, headers={'Location': '/login'}
                    )(environ, start_response)

                state = user_workflow(user).get_state()
                if state is user_workflow.states.pending:
                    if environ['PATH_INFO'] != '/register':
                        # user needs to finish the registration
                        return Response.create(
                            302, headers={'Location': '/register'}
                        )(environ, start_response)
                elif state in self.forbidden_states:
                    return Response.create(403)(environ, start_response)

            return app(environ, start_response)

        return auth_application_wrapper


def plugin(app, config, user_model=User, name="authentication"):
    user = user_model(app.database.session)
    auth = Auth(user, config.env)
    app.plugins.register(auth, name=name)
    app.middlewares.register(auth, order=0)  # very first.
    return app
