from webtest import TestApp


def test_flash(application):
    app = TestApp(application)
    request = app.app.request_factory(
        app.app, {"REQUEST_METHOD": "GET", "docmanager.test.session": {}}, "/"
    )
    flash_manager = app.app.plugins.get("flash").source(request)
    assert len([x for x in flash_manager]) == 0
    flash_manager.add(body="Hello World")
    flash_messages = [x for x in flash_manager]
    assert len(flash_messages) == 1
    message = flash_messages[0]
    assert message.type == "info"
    assert message.body == "Hello World"

    #  Grab the Messages a 2'nd times
    flash_messages = [x for x in flash_manager]
    assert len(flash_messages) == 0
