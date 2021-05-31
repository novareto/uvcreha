from horseman.types import Environ


class TwoFA:

    __slots__ = ('config',)

    def __init__(self, config):
        self.config = config

    def check_twoFA(self, environ: Environ):
        session = environ[self.config.session]
        return session.get('twoFA', False)

    def validate_twoFA(self, environ: Environ):
        session = environ[self.config.session]
        session['twoFA'] = True
