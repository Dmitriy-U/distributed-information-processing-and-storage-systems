import uuid

from sqlalchemy import UUID, Column, ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import relationship

from .database import Base


class File(Base):
    __tablename__ = "files"

    path_name = Column(String, unique=True, primary_key=True)

    blocks = relationship(
        "Block",
        cascade="all, delete",
        back_populates="file",
        passive_deletes=True
    )


class Storage(Base):
    __tablename__ = "storages"

    address = Column(String, unique=True, primary_key=True)

    blocks = relationship("Block", cascade="all,delete", back_populates="storage")


class Block(Base):
    __tablename__ = "blocks"

    __mapper_args__ = {
        'polymorphic_identity': 'block',
        'confirm_deleted_rows': False
    }

    uuid = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    id = Column(String)
    file_path_name = Column(String, ForeignKey("files.path_name", ondelete="CASCADE"))
    storage_address = Column(String, ForeignKey("storages.address"))

    file = relationship("File", back_populates="blocks")
    storage = relationship("Storage", back_populates="blocks")

    __table_args__ = (
        UniqueConstraint('id', 'file_path_name', name='_file_path_name_block_id'),
    )
