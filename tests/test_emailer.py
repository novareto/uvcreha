from uvcreha.emailer import SecureMailer
from email.mime.multipart import MIMEMultipart


def test_emailer():
    mailer = SecureMailer(
        config=dict(
            host="localhost", user="", password="", port="", emitter="web@web.de"
        )
    )
    assert isinstance(mailer, SecureMailer)

    mail = mailer.email("ck@novareto.de", "SUBJECT", "TEXT")
    assert isinstance(mail, MIMEMultipart)
