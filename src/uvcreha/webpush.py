import json
from datetime import datetime, timedelta
from typing import NamedTuple, Optional
from pywebpush import webpush, WebPushException


class Webpush(NamedTuple):
    claims: dict
    private_key: str
    public_key: str

    def send(self, token: str, message: str) -> Optional[str]:
        info = json.loads(token)
        ts = datetime.timestamp(datetime.now() + timedelta(hours=1))
        claims = {**self.claims, "exp": ts}
        try:
            webpush(
                subscription_info=info,
                data=message,
                vapid_private_key=self.private_key,
                vapid_claims=claims,
            )
        except WebPushException as e:
            return str(e)
