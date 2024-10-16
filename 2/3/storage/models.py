import uuid

from sqlalchemy import UUID, Column, ForeignKey, String, LargeBinary, UniqueConstraint
from sqlalchemy.orm import relationship

from .database import Base


class File(Base):
    __tablename__ = "files"

    path_name = Column(String, unique=True, primary_key=True)

    blocks = relationship(
        "Block",
        cascade="all,delete",
        back_populates="file",
        passive_deletes=True
    )


class Block(Base):
    __tablename__ = "blocks"

    uuid = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    id = Column(String)
    data = Column(LargeBinary)
    file_path_name = Column(String, ForeignKey("files.path_name", ondelete="CASCADE"))

    file = relationship("File", back_populates="blocks")

    __table_args__ = (
        UniqueConstraint('id', 'file_path_name', name='_file_path_name_block_id'),
    )
