import socket
import json
# import asyncio

from fastapi import FastAPI, Depends, Request
from fastapi.responses import Response

from .constants import IP_ADDRESS, UDP_PORT
from .database import SessionLocal, Base, engine
from .crud import create_node_if_not_exist
from .helpers import get_self_ip_address, get_hash, to_camel_case
from .responses import OctetStreamResponse
from .schemas import NodeRequestData

app = FastAPI()

Base.metadata.create_all(bind=engine)


# class SyslogProtocol(asyncio.DatagramProtocol):
#     def __init__(self):
#         super().__init__()
#
#     def connection_made(self, transport):
#         self.transport = transport
#
#     def datagram_received(self, data, addr):
#         # Here is where you would push message to whatever methods/classes you want.
#         print(f"Received Syslog message: {data}")


async def parse_body(request: Request):
    data: bytes = await request.body()
    return data


@app.put("/nodes", tags=["Ноды"])
async def nodes_update(nodes: NodeRequestData):
    print('-->', nodes)
    # Will have done


@app.get("/keys/{key_hash}", tags=["Ключи"], response_class=OctetStreamResponse)
async def keys_get(key_hash: int):
    print('-->', key_hash)
    return b"TODO"


@app.post("/keys/{key_hash}", tags=["Ключи"], status_code=201, response_model=None)
async def keys_set(key_hash: int, data: bytes = Depends(parse_body)) -> Response:
    print('-->', key_hash)
    # Will have done
    return Response(None)


@app.on_event("startup")
async def startup_event():
    ip_address = get_self_ip_address()

    # Сохранение текущей ноды
    with SessionLocal() as session:
        create_node_if_not_exist(session, ip_address, get_hash(ip_address.encode()))

    # Запуск прослушивания широковещания порта
    # loop = asyncio.get_event_loop()
    # datagram_endpoint = loop.create_datagram_endpoint(
    #     SyslogProtocol,
    #     local_addr=(IP_ADDRESS, UDP_PORT,),
    #     allow_broadcast=True
    # )
    # loop.run_until_complete(datagram_endpoint)
    # loop.run_forever()

    # Отправка информации о себе
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    advertise = {"ip": ip_address, "key": "LABORATORY_4"}
    sock.sendto(json.dumps(advertise).encode(), (IP_ADDRESS, UDP_PORT))
