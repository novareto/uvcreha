import datetime
from typing import List

from pydantic_sqlalchemy import sqlalchemy_to_pydantic
from sqlalchemy import create_engine
from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from roughrider.validation.types import Validatable
from docmanager.request import Request


Base = declarative_base()


class Database:

    __slots__ = ('_session',)

    def __init__(self, url: str='http://localhost:8529', **config):
        engine = create_engine(url, **config)
        Base.metadata.create_all(engine)
        self._session = sessionmaker(bind=engine)

    def new_session(self):
        return self._session()


class SQLUser(Base, Validatable):

    __tablename__ = 'users'
    __route_key__ = 'userid'

    username = Column(String, primary_key=True)
    password = Column(String)

    folders = relationship(
        "SQLFolder", back_populates="user",
        cascade="all, delete, delete-orphan"
    )

    @classmethod
    def instanciate(cls, request: Request, **bindable):
        key = bindable[cls.__route_key__]
        if (obj := request.database_session.query(cls).get(key)) is not None:
            return obj
        raise LookupError()


class SQLFolder(Base):

    __tablename__ = 'folders'

    az = Column(String, primary_key=True)
    creation_date = Column(DateTime, default=datetime.datetime.utcnow)
    modification_date = Column(DateTime, default=datetime.datetime.utcnow)
    username = Column(Integer, ForeignKey("users.username"))

    user = relationship("SQLUser", back_populates="folders")
    documents = relationship(
        "SQLDocument", back_populates="folder",
        cascade="all, delete, delete-orphan"
    )


class SQLDocument(Base):

    __tablename__ = 'documents'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    state = Column(String)
    content_type = Column(String)
    creation_date = Column(DateTime, default=datetime.datetime.utcnow)
    modification_date = Column(DateTime, default=datetime.datetime.utcnow)
    folder_id = Column(Integer, ForeignKey("folders.az"))

    folder = relationship("SQLFolder", back_populates="documents")


User = sqlalchemy_to_pydantic(SQLUser)
Folder = sqlalchemy_to_pydantic(SQLFolder)
Document = sqlalchemy_to_pydantic(SQLDocument)
