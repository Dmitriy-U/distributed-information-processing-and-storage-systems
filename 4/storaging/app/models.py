from sqlalchemy import Column, String, BigInteger, LargeBinary

from .database import Base


class Node(Base):
    __tablename__ = "nodes"

    hash = Column(BigInteger, unique=True, primary_key=True)
    ip_address = Column(String, unique=True)


class DataItem(Base):
    __tablename__ = "storage"

    hash = Column(BigInteger, unique=True, primary_key=True)
    data = Column(LargeBinary)
