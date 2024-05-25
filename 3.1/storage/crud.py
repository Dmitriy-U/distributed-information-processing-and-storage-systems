from sqlalchemy import delete
from sqlalchemy.orm import Session

from . import models, schemas


def get_file(db: Session, path_name: str):
    return db.query(models.File).filter(models.File.path_name == path_name).first()


def get_or_create_file(db: Session, path_name: str):
    exist_file = db.query(models.File).filter(models.File.path_name == path_name).first()

    if exist_file:
        return exist_file
    else:
        db_file = models.File(path_name=path_name)
        db.add(db_file)
        db.commit()
        db.refresh(db_file)
        return db_file


def delete_file(db: Session, path_name: str):
    file = get_file(db, path_name)

    if file:
        db.delete(file)

        db.execute(delete(models.Block).where(models.Block.file_path_name == path_name))


def get_block(db: Session, block_id: str, file_path_name: str):
    return db.query(models.Block).filter(models.Block.id == block_id).filter(
        models.Block.file_path_name == file_path_name).first()


def create_block(db: Session, block_id: str, block_data: bytes, file_path_name: str):
    file = get_or_create_file(db, file_path_name)

    db_block = models.Block(
        id=block_id,
        file_path_name=file.path_name,
        data=block_data,
    )
    db.add(db_block)
    db.commit()
    db.refresh(db_block)

    return db_block


def update_block(db: Session, block_id: str, block_data: bytes, file_path_name: str):
    block = get_block(db, block_id, file_path_name)

    if block:
        block.data = block_data
        db.refresh(block)
        return block

    return None
