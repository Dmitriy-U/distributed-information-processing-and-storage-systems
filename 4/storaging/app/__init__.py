import socket
import json

from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, Depends
from fastapi.responses import Response
from sqlalchemy.orm import Session

from .constants import IP_ADDRESS, UDP_PORT, APP_KEY, IP_ADDRESS_BROADCAST
from .database import SessionLocal, Base, engine, get_db
from .crud import create_node_if_not_exist, create_or_update_data_item
from .helpers import get_self_ip_address, get_hash, to_camel_case
from .logger import logger
from .responses import OctetStreamResponse
from .schemas import NodeRequestData
from .udp_listener import UDPNodeSynchronizationLoop

advertise_listener_thread = UDPNodeSynchronizationLoop(app_key=APP_KEY, host=(IP_ADDRESS_BROADCAST, UDP_PORT))


@asynccontextmanager
async def lifespan(app):
    logger.info('sub startup')
    ip_address = get_self_ip_address()
    logger.info(f"Собственный ip адрес: {ip_address}")

    # Сохранение текущей ноды
    with SessionLocal() as session:
        create_node_if_not_exist(session, ip_address, get_hash(ip_address.encode()))

    # Отправка информации о себе
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    advertise = {"ip": ip_address, "key": APP_KEY}
    sock.sendto(json.dumps(advertise).encode(), (IP_ADDRESS_BROADCAST, UDP_PORT))

    # Запуск прослушивания
    advertise_listener_thread.start()
    logger.info("Запущено прослушивание порта синхронизации")
    yield
    logger.info("sub shutdown")
    # FIXME: Ошибка при закрытии asyncio лупа
    # udp_thread.stop()
    pass


app = FastAPI(lifespan=lifespan)

Base.metadata.create_all(bind=engine)


class RawResponse(Response):
    media_type = "binary/octet-stream"

    def render(self, content: bytes) -> bytes:
        return bytes([b ^ 0x54 for b in content])


@app.put("/nodes", tags=["Ноды"], summary="Обновление нод")
async def nodes_update(nodes: NodeRequestData):
    logger.info(f'Nodes --> {str(nodes)}')
    # Will have done
    return Response(201)


@app.get("/keys/{key_hash}", tags=["Ключи"], response_class=OctetStreamResponse, summary="Получить данные ключа")
async def get_key(key_hash: int):
    logger.info(f'Get key --> {str(key_hash)}')
    return Response(200)


@app.post("/keys/{key_hash}", tags=["Ключи"], status_code=201, summary="Записать данные ключа")
async def keys_set(key_hash: int, request: Request, db: Session = Depends(get_db)):
    data = b''
    async for chunk in request.stream():
        data += chunk
    # TODO: Will have done
    create_or_update_data_item(db, key_hash, data)

    return Response(status_code=201)
