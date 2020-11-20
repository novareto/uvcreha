def test_flash(web_app):
    request = web_app.request_factory(web_app, {
        "REQUEST_METHOD": "GET",
        "docmanager.test.session": {}
    }, "/")

    flash_manager = request.utilities.get('flash')
    assert flash_manager is None

    web_app.notify('request_created', web_app, request)
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
