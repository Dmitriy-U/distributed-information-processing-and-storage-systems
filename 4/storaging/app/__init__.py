import socket
import json

from fastapi import FastAPI

from helpers import get_self_ip_address, get_hash

from .crud import create_node

UDP_PORT = 9000
IP_ADDRESS = get_self_ip_address()


app = FastAPI()


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/items/{item_id}")
def read_item(item_id: int, q: str | None = None):
    return {"item_id": item_id, "q": q}


@app.on_event("startup")
async def startup_event():
    ip_address = get_self_ip_address()
    create_node()
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    advertise = {
        "hash": get_hash(ip_address.encode()),
        "key": "test"
    }
    sock.sendto(bytes(json.dumps(advertise), "utf-8"), ('127.0.0.2', UDP_PORT))
