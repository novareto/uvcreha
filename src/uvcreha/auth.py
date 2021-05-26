from horseman.types import Environ
from horseman.response import Response
from uvcreha.workflow import user_workflow
from uvcreha import contenttypes


class Auth:

    twoFA: bool
    unprotected: set = {'/login', '/webpush'}
    forbidden_states: set = {
        user_workflow.states.inactive,
        user_workflow.states.closed
    }

    def __init__(self, connector, config, twoFA: bool = True):
        self.connector = connector
        self.config = config
        self.twoFA = twoFA

    def from_credentials(self, credentials: dict):
        db = self.connector.get_database()
        binding = contenttypes.registry['user'].bind(db)
        # We use either loginname or email
        user = binding.find_one(
            loginname=credentials['loginname'],
            password=credentials['password']
        )
        if user is not None:
            return user
        return binding.find_one(
            email=credentials['loginname'],
            password=credentials['password']
        )

    def identify(self, environ: Environ):
        if (user := environ.get(self.config.user)) is not None:
            return user
        session = environ[self.config.session]
        if (user_key := session.get(self.config.user, None)) is not None:
            db = self.connector.get_database()
            binding = contenttypes.registry['user'].bind(db)
            user = environ[self.config.user] = binding.fetch(user_key)
            return user
        return None

    def remember(self, environ: Environ, user):
        session = environ[self.config.session]
        session[self.config.user] = user['uid']
        environ[self.config.user] = user

    def check_twoFA(self, environ: Environ):
        session = environ[self.config.session]
        return session.get('twoFA', False)

    def validate_twoFA(self, environ: Environ):
        session = environ[self.config.session]
        session['twoFA'] = True

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
                if user.state is user_workflow.states.pending:
                    if environ['PATH_INFO'] != '/register':
                        # user needs to finish the registration
                        return Response.create(
                            302, headers={'Location': '/register'}
                        )(environ, start_response)
                elif user.state in self.forbidden_states:
                    return Response.create(403)(environ, start_response)
                if self.twoFA and not self.check_twoFA(environ):
                    if environ['PATH_INFO'] != '/2FA':
                        # We could generate the TOTP as soon as we reach here
                        # app.notify('2FA', app, user)
                        return Response.create(
                            302, headers={'Location': '/2FA'}
                    )(environ, start_response)
            return app(environ, start_response)

        return auth_application_wrapper
