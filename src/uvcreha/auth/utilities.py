from horseman.types import Environ


class TwoFA:

    __slots__ = ('session_key',)

    def __init__(self, session_key):
        self.session_key = session_key

    def check_twoFA(self, environ: Environ):
        session = environ[self.session_key]
        return session.get('twoFA', False)

    def validate_twoFA(self, environ: Environ):
        session = environ[self.session_key]
        session['twoFA'] = True
