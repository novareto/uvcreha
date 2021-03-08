import pytest
from uvcreha.models import User, File, Document
from reiter.arango.connector import Connector


@pytest.fixture(scope="session")
def db_init(arango_config):
    connector = Connector(**arango_config._asdict())
    db = connector.get_database()
    db.db.create_collection(User.__collection__)
    db.db.create_collection(File.__collection__)
    db.db.create_collection(Document.__collection__)
    yield connector
    db.db.delete_collection(User.__collection__)
    db.db.delete_collection(File.__collection__)
    db.db.delete_collection(Document.__collection__)
