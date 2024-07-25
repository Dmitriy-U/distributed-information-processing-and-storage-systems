from sqlalchemy import Column, String, Integer, LargeBinary

from .database import Base


class Node(Base):
    __tablename__ = "nodes"

    hash = Column(Integer, unique=True, primary_key=True)
    ip = Column(String, unique=True)


class DataRow(Base):
    __tablename__ = "storage"

    hash = Column(Integer, unique=True, primary_key=True)
    data = Column(LargeBinary)
