from horseman.types import WSGICallable


def flash_messages(session_key):
    from uvcreha.flash import SessionMessages

    def flash(environ):
        session = environ[session_key]
        return SessionMessages(session)

    return flash


def vhm_middleware(**config) -> WSGICallable:
    import functools
    from repoze.vhm.middleware import VHMExplicitFilter

    return functools.partial(VHMExplicitFilter, **config)


def fanstatic_middleware(**config) -> WSGICallable:
    import fanstatic
    import functools

    return functools.partial(fanstatic.Fanstatic, **config)


def session_middleware(
        cache, cookie_secret, cookie_name, environ_key) -> WSGICallable:
    import cromlech.session
    import cromlech.sessions.file

    handler = cromlech.sessions.file.FileStore(cache, 3000)
    manager = cromlech.session.SignedCookieManager(
        cookie_secret,
        handler,
        cookie=cookie_name
    )
    return cromlech.session.WSGISessionManager(manager, environ_key=environ_key)


def webpush_plugin(private_key, public_key, vapid_claims):
    from uvcreha.webpush import Webpush

    with open(private_key) as fd:
        privkey = fd.readline().strip("\n")

    with open(public_key) as fd:
        pubkey = fd.read().strip("\n")

    return Webpush(
        private_key=privkey,
        public_key=pubkey,
        claims=vapid_claims
    )


def twilio_plugin(account_sid, auth_token):
    from twilio.rest import Client
    return Client(account_sid, auth_token)
