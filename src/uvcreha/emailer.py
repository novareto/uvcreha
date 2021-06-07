import smtplib
import functools
from typing import NamedTuple
from contextlib import contextmanager
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


class SMTPConfiguration(NamedTuple):
    user: str
    password: str
    emitter: str
    port: int = 25
    host: str = "localhost"


class SecureMailer:

    config: SMTPConfiguration
    debug: bool

    __slots__ = ("config", "debug")

    def __init__(self, **config):
        self.config = SMTPConfiguration(**config)
        self.debug = False

    @staticmethod
    def format_email(_from, _to, subject, text, html=None):
        msg = MIMEMultipart("alternative")
        msg["From"] = _from
        msg["To"] = _to
        msg["Subject"] = subject
        msg.set_charset("utf-8")

        part1 = MIMEText(text, "plain")
        part1.set_charset("utf-8")
        msg.attach(part1)

        if html is not None:
            part2 = MIMEText(html, "html")
            part2.set_charset("utf-8")
            msg.attach(part2)

        return msg

    def email(self, recipient, subject, text, html=None):
        return self.format_email(self.config.emitter, recipient, subject, text, html)

    @contextmanager
    def smtp(self):
        server = smtplib.SMTP(self.config.host, self.config.port)
        server.set_debuglevel(self.debug)

        # identify ourselves, prompting server for supported features
        server.ehlo()

        # If we can encrypt this session, do it
        if server.has_extn("STARTTLS"):
            server.starttls()
            server.ehlo()  # re-identify ourselves over TLS connection
        if self.config.user:
            server.login(self.config.user, self.config.password)
        try:
            yield functools.partial(server.sendmail, self.config.emitter)
        finally:
            server.close()
