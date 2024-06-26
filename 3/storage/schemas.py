from pydantic import BaseModel


class BlockBase(BaseModel):
    id: str
    data: bytes


class Block(BlockBase):
    file_path_name: str

    class Config:
        from_attributes = True


class FileBase(BaseModel):
    path_name: str
    block_count: int


class File(FileBase):
    items: list[Block] = []

    class Config:
        from_attributes = True
