from datetime import date
from docmanager.models import Base


class Event(Base):
    content_type: str = "Event"
    subject: str
