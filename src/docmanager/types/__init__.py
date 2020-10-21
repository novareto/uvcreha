# Sample Type Implementation


from docmanager.app import application
from datetime import date
from docmanager.models import Base


@application.register_type(name="event")
class Event(Base):
    content_type: str = "Event"
    subject: str
