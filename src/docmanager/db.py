from collections import namedtuple
from cached_property import cached_property
from arango import ArangoClient
from functools import cached_property


DB_CONFIG = namedtuple('DB', ['user', 'password', 'database'])


class Database:

    def __init__(self, url: str='http://localhost:8529', **config):
        self.config = DB_CONFIG(**config)
        self.client = ArangoClient(url)

    def ensure_database(self):
        sys_db = self.client.db(
            '_system',
            username=self.config.user,
            password=self.config.password
        )
        if not sys_db.has_database(self.config.database):
            sys_db.create_database(self.config.database)

    @cached_property
    def connector(self):
        return self.client.db(
            self.config.database,
            username=self.config.user,
            password=self.config.password
        )

    def query(self, aql: str, *args, **kwargs):
        return self.connector.AQLQuery(aql, *args, **kwargs)

    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not isinstance(v, cls):
            raise TypeError('Database required')
        return v

    @classmethod
    def __modify_schema__(cls, field_schema):
        field_schema.update({
            'title': 'Database'
        })
