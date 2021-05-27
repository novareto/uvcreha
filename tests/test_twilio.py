def test_twilio(root, session):
    from twilio.rest import Client

    web_app = root['/']
    twilio = web_app.utilities.get('twilio')
    assert twilio is not None
    assert isinstance(twilio, Client) is True
