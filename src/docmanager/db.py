from collections import namedtuple
from cached_property import cached_property
from arango import ArangoClient
from functools import cached_property
from roughrider.validation.types import Validatable
from docmanager.request import Request
import orjson


DB_CONFIG = namedtuple('DB', ['user', 'password', 'database'])


class Database:

    def __init__(self, url: str='http://localhost:8529', **config):
        self.config = DB_CONFIG(**config)
        self.client = ArangoClient(url, serializer=orjson.dumps, deserializer=orjson.loads)

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

    def add_files(self, userid, data):
        documents = self.connector.collection('documents')
        ownership = self.connector.graph('ownership')
        metadata = files.insert(data)
        own = ownership.edge_collection('own_files')
        own.insert({
            '_key': f"{userid}-{metadata['_key']}",
            '_from': f"users/{userid}",
            '_to': metadata['_id'],
        })
        return metadata['_key']

    def add_document(self, file_id, data):
        documents = self.connector.collection('documents')
        ownership = self.connector.graph('ownership')
        metadata = documents.insert(data)
        own = ownership.edge_collection('own_files')
        own.insert({
            '_key': f"{file_id}-{metadata['_key']}",
            '_from': f"files/{file_id}",
            '_to': metadata['_id'],
        })
        return metadata['_key']

def create_graph(db: Database):
    if db.connector.has_graph('ownership'):
        ownership = db.connector.graph('ownership')
    else:
        ownership = db.connector.create_graph('ownership')

    # Vertices
    if not ownership.has_vertex_collection('users'):
        ownership.create_vertex_collection('users')
    if not ownership.has_vertex_collection('files'):
        ownership.create_vertex_collection('files')
    if not ownership.has_vertex_collection('documents'):
        ownership.create_vertex_collection('documents')

    # Edges
    if not ownership.has_edge_definition('own'):
        ownership.create_edge_definition(
            edge_collection='own',
            from_vertex_collections=['users'],
            to_vertex_collections=['files']
        )
    if not ownership.has_edge_definition('own_files'):
        ownership.create_edge_definition(
            edge_collection='own_files',
            from_vertex_collections=['files'],
            to_vertex_collections=['documents']
        )
