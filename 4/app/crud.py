from sqlalchemy.orm import Session
from itertools import chain

from . import models


def get_node_ip_list(db: Session) -> list[models.Node.ip]:
    result = db.query(models.Node.ip).all()
    return list(chain(*result))


def get_nodes(db: Session) -> list[models.Node]:
    return db.query(models.Node).all()


def create_node_if_not_exist(db: Session, ip: str, ip_hash: int):
    node = db.query(models.Node).filter(models.Node.ip == ip).first()

    if node is not None:
        return

    node = models.Node(ip=ip, hash=ip_hash)
    db.add(node)
    db.commit()
    db.refresh(node)


def create_or_update_data_item(db: Session, key_hash: int, data: bytes):
    data_item = db.query(models.DataRow).filter(models.DataRow.key_hash == key_hash).first()

    if data_item is None:
        data_item = models.DataRow(hash=key_hash, data=data)
        db.add(data_item)
        db.commit()
        db.refresh(data_item)
    else:
        data_item.key_hash = key_hash
        data_item.data = data
        db.commit()
        db.refresh(data_item)


def get_data_item(db: Session, key_hash: int) -> models.DataRow | None:
    return db.query(models.DataRow).filter(models.DataRow.key_hash == key_hash).first()


def delete_data_item(db: Session, key_hash: int):
    data_item = db.query(models.DataRow).filter(models.DataRow.key_hash == key_hash).first()

    if data_item is not None:
        db.delete(data_item)
        db.commit()
        db.refresh(data_item)
