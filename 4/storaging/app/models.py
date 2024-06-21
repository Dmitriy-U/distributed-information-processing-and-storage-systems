from sqlalchemy import Column, String, Integer, LargeBinary

from .database import Base


class Node(Base):
    __tablename__ = "nodes"

    ip_hash = Column(Integer, unique=True, primary_key=True)
    ip_address = Column(String, unique=True)


class DataRow(Base):
    __tablename__ = "storage"

    key_hash = Column(Integer, unique=True, primary_key=True)
    data = Column(LargeBinary)
