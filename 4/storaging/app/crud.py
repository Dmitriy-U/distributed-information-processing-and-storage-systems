from sqlalchemy import delete
from sqlalchemy.orm import Session

from helpers import get_hash

from . import models, schemas


def create_node(db: Session, ip_address: str):
    node = models.Node(
        ip_address=ip_address,
        hash=get_hash(ip_address.encode())
    )
    db.add(node)
    db.commit()
    db.refresh(node)

    return node
