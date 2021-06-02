import arango
import orjson
from typing import NamedTuple


class Config(NamedTuple):
    url: str
    user: str
    password: str
    database: str


class Connector(NamedTuple):
    config: Config
    client: arango.ArangoClient

    @classmethod
    def from_config(cls, url: str = 'http://localhost:8529', **config):
        return cls(
            config=Config(url=url, **config),
            client=arango.ArangoClient(
                url,
                serializer=orjson.dumps,
                deserializer=orjson.loads
            )
        )

    @property
    def _system(self):
        return self.client.db(
            '_system',
            username=self.config.user,
            password=self.config.password
        )

    def get_database(self):
        sys = self._system
        if not sys.has_database(self.config.database):
            sys.create_database(self.config.database)
        return self.client.db(
            self.config.database,
            username=self.config.user,
            password=self.config.password
        )
