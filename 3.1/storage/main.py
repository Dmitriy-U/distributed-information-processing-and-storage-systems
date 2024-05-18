from fastapi import FastAPI, File, Request, Response

class RawResponse(Response):
    media_type = "binary/octet-stream"

    def render(self, content: bytes) -> bytes:
        return bytes([b ^ 0x54 for b in content])

app = FastAPI(default_response_class=RawResponse)


@app.get("/{file_path}/{block_id}")
async def read_block_of_file(file_path: str, block_id: str):
    return RawResponse(content=b"1001")


@app.post("/{file_path}/{block_id}")
async def write_block_of_file(file_path: str, block_id: str, request: Request):
    data: bytes = await request.body()
    print(data)
    return RawResponse(content=b"")


@app.put("/{file_path}/{block_id}")
async def change_block_of_file(file_path: str, block_id: str,  request: Request):
    data: bytes = await request.body()
    print(data)
    return RawResponse(content=b"")


@app.delete("/{file_path}", response_class=Response)
async def delete_file(file_path: str):
    return Response(status_code=201)
