from sqlalchemy import delete, distinct
from sqlalchemy.orm import Session

from .models import File, Block, Storage


def get_file(db: Session, path_name: str):
    return db.query(File).filter(File.path_name == path_name).first()


def db_get_file_blocks(db: Session, path_name: str):
    return db.query(Block).filter(Block.file_path_name == path_name).join(
        Storage,
        Block.storage_address == Storage.address,
        isouter=True
    ).all()


def db_get_file_storages(db: Session, path_name: str):
    return db.query(Block.storage_address.distinct()).filter(
        Block.file_path_name == path_name
    ).all()


def db_delete_file(db: Session, path_name: str):
    file = db.query(File).filter(File.path_name == path_name).first()

    if file is not None:
        print(file.blocks)
        db.delete(file)
        db.execute(delete(Block).where(Block.file_path_name == path_name))
        db.commit()
