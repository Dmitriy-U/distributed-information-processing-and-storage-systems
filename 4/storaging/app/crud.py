from sqlalchemy.orm import Session

from . import models


def create_node_if_not_exist(db: Session, ip_address: str, ip_hash: int):
    node = db.query(models.Node).filter(models.Node.ip_address == ip_address).first()

    if node is not None:
        return

    node = models.Node(ip_address=ip_address, ip_hash=ip_hash)
    db.add(node)
    db.commit()
    db.refresh(node)


def create_or_update_data_item(db: Session, key_hash: int, data: bytes):
    data_item = db.query(models.DataRow).filter(models.DataRow.key_hash == key_hash).first()

    if data_item is None:
        data_item = models.DataRow(key_hash=key_hash, data=data)
        db.add(data_item)
        db.commit()
        db.refresh(data_item)
    else:
        data_item.key_hash = key_hash
        data_item.data = data
        db.commit()
        db.refresh(data_item)
