from sqlalchemy import delete
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


def db_get_file_block(db: Session, path_name: str, block_id: str) -> Block | None:
    try:
        return db.query(Block).where(Block.file_path_name == path_name).where(Block.id == block_id).join(
            Storage,
            Block.storage_address == Storage.address,
            isouter=True
        ).one()
    except Exception as e:
        return None


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


def db_insert_file_if_not_exist(db: Session, path_name: str):
    file = db.query(File).filter(File.path_name == path_name).first()

    if file is None:
        file = File(path_name=path_name)
        db.add(file)
        db.commit()


def db_insert_storage_if_not_exist(db: Session, storage_address: str):
    storage = db.query(Storage).filter(Storage.address == storage_address).first()

    if storage is None:
        storage = Storage(address=storage_address)
        db.add(storage)
        db.commit()


def db_bulk_insert_storages(db: Session, storages: list[Storage]):
    db.bulk_insert_mappings(Storage, [{"address": storage.address} for storage in storages])
    db.commit()


def db_bulk_insert_blocks(db: Session, blocks: list[Block]):
    db.bulk_insert_mappings(Block, [
        {"id": block.id, "file_path_name": block.file_path_name, "storage_address": block.storage_address} for block in
        blocks])
    db.commit()
