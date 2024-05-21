import uuid

from sqlalchemy import UUID, Column, ForeignKey, String, LargeBinary
from sqlalchemy.orm import relationship

from .database import Base


class File(Base):
    __tablename__ = "files"

    path_name = Column(String, unique=True, primary_key=True)

    blocks = relationship(
        "Block",
        cascade="all,delete",
        back_populates="file"
    )


class Block(Base):
    __tablename__ = "blocks"

    uuid = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    id = Column(String)
    data = Column(LargeBinary)
    file_path_name = Column(String, ForeignKey("files.path_name"))

    file = relationship("File", back_populates="blocks")
