from sqlalchemy.orm import Session

from .models import File, Block, Storage


def get_file(db: Session, path_name: str):
    return db.query(File).filter(File.path_name == path_name).first()


def get_file_blocks(db: Session, path_name: str):
    return db.query(Block).filter(Block.file_path_name == path_name).join(
        Storage,
        Block.storage_address == Storage.address,
        isouter=True
    ).all()
