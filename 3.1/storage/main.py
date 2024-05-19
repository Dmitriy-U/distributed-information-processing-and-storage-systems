from fastapi import FastAPI, File, Request, Depends
from fastapi.responses import Response
from sqlalchemy.orm import Session

from . import models, crud
from .database import SessionLocal, engine


class RawResponse(Response):
    media_type = "binary/octet-stream"

    def render(self, content: bytes) -> bytes:
        return bytes([b ^ 0x54 for b in content])

models.Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


app = FastAPI()


@app.get("/{file_path_name}/{block_id}", response_class=RawResponse)
async def read_block_of_file(file_path_name: str, block_id: str, db: Session = Depends(get_db)):
    block = crud.get_block(db, block_id, file_path_name)
    
    if block:
        return RawResponse(content=block.data)
    else:
        return Response(status_code=404)


@app.post("/{file_path_name}/{block_id}")
async def write_block_of_file(file_path_name: str, block_id: str, request: Request, db: Session = Depends(get_db)):
    block_data = await request.body()
    crud.create_block(db, block_id, block_data, file_path_name)

    return Response(status_code=201)


@app.put("/{file_path_name}/{block_id}")
async def change_block_of_file(file_path_name: str, block_id: str,  request: Request, db: Session = Depends(get_db)):
    block_data = await request.body()
    crud.update_block(db, block_id, block_data, file_path_name)

    return Response(status_code=201)


@app.delete("/{file_path_name}", response_class=Response)
async def delete_file(file_path_name: str, db: Session = Depends(get_db)):
    crud.delete_file(db, path_name=file_path_name)
    return Response(status_code=200)
