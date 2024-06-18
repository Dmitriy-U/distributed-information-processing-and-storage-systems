from sqlalchemy.orm import Session

from . import models


def create_node_if_not_exist(db: Session, ip_address: str, hash: int):
    node = db.query(models.Node).filter(models.Node.ip_address == ip_address).first()

    if node is not None:
        return

    node = models.Node(ip_address=ip_address, hash=hash)
    db.add(node)
    db.commit()
    db.refresh(node)
