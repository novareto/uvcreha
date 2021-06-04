def test_twilio(webapp, session):
    from twilio.rest import Client

    app = webapp.__wrapped__
    twilio = app.utilities.get('twilio')
    assert twilio is not None
    assert isinstance(twilio, Client) is True
