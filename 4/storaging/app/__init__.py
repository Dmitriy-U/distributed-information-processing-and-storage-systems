import socket
import json
import asyncio
from asyncio import BaseProtocol

from threading import Thread, Event
from typing import Callable, Generator, Any

from fastapi import FastAPI, Request, Depends
from fastapi.responses import Response
from sqlalchemy.orm import Session

from .constants import IP_ADDRESS, UDP_PORT
from .database import SessionLocal, Base, engine, get_db
from .crud import create_node_if_not_exist, create_or_update_data_item
from .helpers import get_self_ip_address, get_hash, to_camel_case
from .responses import OctetStreamResponse
from .schemas import NodeRequestData

app = FastAPI()

Base.metadata.create_all(bind=engine)


class UDPProtocol(BaseProtocol):
    def __init__(self, get_database: Callable[[], Generator[Session, Any, None]]):
        self.transport = None
        self.get_db = get_database

    def connection_made(self, transport):
        self.transport = transport

    def datagram_received(self, data, addr):
        message = data.decode()
        # TODO: Доделать получение
        print(self.get_db)
        print('Received %r from %s' % (message, addr))


class BackgroundTasks(Thread):
    def __init__(self, get_database: Callable[[], Generator[Session, Any, None]], *args, **kwargs):
        super(BackgroundTasks, self).__init__(*args, **kwargs)

        self._stop_event = Event()
        self._loop = None
        self._transport = None
        self._get_db = get_database

    def run(self, *args, **kwargs):
        self._loop = asyncio.new_event_loop()
        listen = self._loop.create_datagram_endpoint(lambda: UDPProtocol(get_database=self._get_db), local_addr=(IP_ADDRESS, UDP_PORT), allow_broadcast=True)
        transport, protocol = self._loop.run_until_complete(listen)

        self._transport = transport

        try:
            self._loop.run_forever()
        except KeyboardInterrupt:
            pass

        self._transport.close()
        self._loop.close()

    def stop(self):
        print('11111')
        self._transport.close()
        self._loop.stop()
        self._loop.close()
        self._stop_event.set()


t = BackgroundTasks(name="UDP thread", get_database=get_db)


class RawResponse(Response):
    media_type = "binary/octet-stream"

    def render(self, content: bytes) -> bytes:
        return bytes([b ^ 0x54 for b in content])


@app.put("/nodes", tags=["Ноды"], summary="Обновление нод")
async def nodes_update(nodes: NodeRequestData):
    print('-->', nodes)
    # Will have done


@app.get("/keys/{key_hash}", tags=["Ключи"], response_class=OctetStreamResponse, summary="Получить данные ключа")
async def keys_get(key_hash: int):
    print('-->', key_hash)
    return b"TODO"


@app.post("/keys/{key_hash}", tags=["Ключи"], status_code=201, summary="Записать данные ключа")
async def keys_set(key_hash: int, request: Request, db: Session = Depends(get_db)):
    data = b''
    async for chunk in request.stream():
        data += chunk
    # TODO: Will have done
    create_or_update_data_item(db, key_hash, data)

    return Response(status_code=201)


@app.on_event("startup")
async def startup_event():
    ip_address = get_self_ip_address()

    # Сохранение текущей ноды
    with SessionLocal() as session:
        create_node_if_not_exist(session, ip_address, get_hash(ip_address.encode()))

    # Отправка информации о себе
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    advertise = {"ip": ip_address, "key": "LABORATORY_4"}
    sock.sendto(json.dumps(advertise).encode(), (IP_ADDRESS, UDP_PORT))

    t.start()


@app.on_event("shutdown")
async def shutdown_event():
    # FIXME: Ошибка при закрытии asyncio лупа
    t.stop()
