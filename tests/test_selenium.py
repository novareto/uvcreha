import pytest
from roughrider.selenium.server import ServerThread


@pytest.mark.usefixtures("browser_driver")
class TestUVCReha:

    @pytest.fixture(scope='class')
    def server(self, webapp):
        server = ServerThread(webapp)
        server.start()
        yield server
        server.stop()

    def test_landingpage(self, server):
        self.driver.get(server.host)
        print(self.driver.title)
