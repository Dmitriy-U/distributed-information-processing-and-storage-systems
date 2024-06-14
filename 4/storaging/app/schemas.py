from pydantic import BaseModel


class Node(BaseModel):
    hash: int
    ip_address: str

    class Config:
        from_attributes = True


class DataItem(BaseModel):
    hash: int
    value: bytes

    class Config:
        from_attributes = True
