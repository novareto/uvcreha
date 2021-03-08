import pytest
import importscan
import tempfile
import uvcreha
from uvcreha.app import api, browser
from uvcreha.fixtures import CONFIG


@pytest.fixture(scope="session")
def api_app(request, arango_config, db_init):
    import omegaconf
    from zope.dottedname import resolve

    if omegaconf.OmegaConf.get_resolver('class') is None:
        omegaconf.OmegaConf.register_resolver("class", resolve.resolve)

    importscan.scan(uvcreha)
    arango = omegaconf.OmegaConf.create({'arango': arango_config._asdict()})
    conf = omegaconf.OmegaConf.merge(CONFIG, arango)
    api.configure(conf)
    return api


@pytest.fixture(scope="session")
def web_app(request, arango_config, db_init):
    import omegaconf
    from zope.dottedname import resolve

    if omegaconf.OmegaConf.get_resolver('class') is None:
        omegaconf.OmegaConf.register_resolver("class", resolve.resolve)

    importscan.scan(uvcreha)
    folder = tempfile.TemporaryDirectory()
    arango = omegaconf.OmegaConf.create({'arango': arango_config._asdict()})
    conf = omegaconf.OmegaConf.merge(CONFIG, arango)
    conf.app.session.cache = folder.name
    browser.configure(conf)
    yield browser
    folder.cleanup()
