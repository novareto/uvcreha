from reiter.application import events


def test_flash(webapp, session):

    app = webapp.__wrapped__
    request = app.request_factory(app, {
        "REQUEST_METHOD": "GET",
        "SCRIPT_NAME": 'flash_test',
        "uvcreha.test.session": session
    }, "/")

    flash_manager = request.utilities.get('flash')
    assert flash_manager is None

    app.notify(events.RequestCreated(app, request))
    flash_manager = request.utilities.get('flash')
    assert flash_manager is not None

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
