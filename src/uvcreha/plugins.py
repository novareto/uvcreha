from pathlib import Path
from horseman.types import WSGICallable


def flash_messages(session_key):
    from uvcreha.flash import SessionMessages

    def flash(environ):
        session = environ[session_key]
        return SessionMessages(session)

    return flash


def session_middleware(
    cache: Path, cookie_secret, cookie_name, environ_key
) -> WSGICallable:
    import cromlech.session
    import cromlech.sessions.file

    handler = cromlech.sessions.file.FileStore(cache, 3000)
    manager = cromlech.session.SignedCookieManager(
        cookie_secret, handler, cookie=cookie_name
    )
    return cromlech.session.WSGISessionManager(manager, environ_key=environ_key)


def webpush_plugin(private_key: Path, public_key: Path, vapid_claims: dict):
    from uvcreha.webpush import Webpush

    with private_key.open("r") as fd:
        privkey = fd.readline().strip("\n")

    with public_key.open("r") as fd:
        pubkey = fd.read().strip("\n")

    return Webpush(private_key=privkey, public_key=pubkey, claims=vapid_claims)
