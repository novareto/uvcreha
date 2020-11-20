from pathlib import Path
import cromlech.session
import cromlech.sessions.file


def session_middleware(config):
    folder = Path("/tmp/sessions")
    handler = cromlech.sessions.file.FileStore(folder, 3000)
    manager = cromlech.session.SignedCookieManager(
        "secret", handler, cookie="my_sid")
    return cromlech.session.WSGISessionManager(
        manager, environ_key=config.session)


def plugin(app, config):
    middleware = session_middleware(config.env)
    app.middlewares.register(middleware, order=1)
    return app
