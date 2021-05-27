from horseman.types import WSGICallable


def fanstatic_middleware(config) -> WSGICallable:
    import fanstatic
    import functools

    return functools.partial(fanstatic.Fanstatic, **config)


def session_middleware(config) -> WSGICallable:
    import cromlech.session
    import cromlech.sessions.file

    handler = cromlech.sessions.file.FileStore(
        config.session.cache, 3000
    )
    manager = cromlech.session.SignedCookieManager(
        config.session.cookie_secret,
        handler,
        cookie=config.session.cookie_name
    )
    return cromlech.session.WSGISessionManager(
        manager, environ_key=config.env.session)


def webpush_plugin(config):
    from uvcreha.webpush import Webpush

    with open(config.private_key) as fd:
        private_key = fd.readline().strip("\n")

    with open(config.public_key) as fd:
        public_key = fd.read().strip("\n")

    return Webpush(
        private_key=private_key,
        public_key=public_key,
        claims=config.vapid_claims
    )


def twilio_plugin(config):
    from twilio.rest import Client

    return Client(config.account_sid, config.auth_token)
