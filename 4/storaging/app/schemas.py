from pydantic import BaseModel

from .helpers import to_camel_case


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


class NodeRequestData(BaseModel):
    ip_list: list[str]

    model_config = {
        "alias_generator": to_camel_case,
        "json_schema_extra": {
            "examples": [
                {
                    "ipList": ["127.0.0.1", "192.168.68.255"],
                }
            ]
        }
    }
