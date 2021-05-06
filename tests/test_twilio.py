def test_twilio(web_app, session):
    from twilio.rest import Client
    twilio = web_app.utilities.get('twilio')
    assert twilio is not None
    assert isinstance(twilio, Client) is True
