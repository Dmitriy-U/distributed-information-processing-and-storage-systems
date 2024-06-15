from sqlalchemy.orm import Session

from . import models

from ..helpers import get_hash


def create_node_if_not_exist(db: Session, ip_address: str):
    node = db.query(models.Node).filter(models.Node.ip_address == ip_address).first()

    if node is not None:
        return

    node = models.Node(
        ip_address=ip_address,
        hash=get_hash(ip_address.encode())
    )
    db.add(node)
    db.commit()
    db.refresh(node)
