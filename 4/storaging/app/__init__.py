import socket
import json

from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, Depends
from fastapi.responses import Response
from sqlalchemy.orm import Session

from .constants import UDP_PORT, APP_KEY, IP_ADDRESS_BROADCAST
from .database import SessionLocal, Base, engine, get_db
from .crud import create_node_if_not_exist, create_or_update_data_item, get_nodes
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


@app.put("/api/internal/nodes", tags=["Внутреннее API"], summary="Обновление нод", status_code=201)
async def nodes_update(nodes: NodeRequestData, db: Session = Depends(get_db)):
    logger.info(f'Nodes update --> {nodes}')
    for ip in nodes.ip_list:
        create_node_if_not_exist(db, ip, get_hash(ip.encode()))


@app.get("/api/internal/keys/{key_hash}", tags=["Внутреннее API"], response_class=OctetStreamResponse, status_code=200, summary="Получить данные ключа")
async def get_key(key_hash: int):
    logger.info(f'Get key --> {str(key_hash)}')
    return Response(200)


@app.post("/api/internal/keys/{key_hash}", tags=["Внутреннее API"], status_code=201, summary="Записать данные ключа")
async def keys_set(key_hash: int, request: Request, db: Session = Depends(get_db)):
    data = b''
    async for chunk in request.stream():
        data += chunk

    create_or_update_data_item(db, key_hash, data)

    return Response(status_code=201)


@app.delete("/api/internal/keys/{key_hash}", tags=["Внутреннее API"], status_code=200, summary="Удалить ключ")
async def keys_delete(key_hash: int, request: Request, db: Session = Depends(get_db)):
    data = b''
    async for chunk in request.stream():
        data += chunk
    # TODO: Will have done
    create_or_update_data_item(db, key_hash, data)

    return Response(status_code=201)


@app.get("/api/external/keys/{key}", tags=["Внешнее API"], response_class=OctetStreamResponse, status_code=200, summary="Получить данные ключа")
async def get_key(key: str, db: Session = Depends(get_db)):
    key_hash = get_hash(key)
    nodes = get_nodes(db)
    # TODO: Will have done
    logger.info(f'Get key --> {str(key_hash)}')
    return Response(200)


@app.post("/api/external/keys/{key}", tags=["Внешнее API"], status_code=201, summary="Записать данные ключа")
async def keys_set(key: str, request: Request, db: Session = Depends(get_db)):
    key_hash = get_hash(key)
    data = b''
    async for chunk in request.stream():
        data += chunk

    create_or_update_data_item(db, key_hash, data)

    return Response(status_code=201)


@app.delete("/api/external/keys/{key}", tags=["Внешнее API"], status_code=200, summary="Удалить ключ")
async def keys_delete(key: int, request: Request, db: Session = Depends(get_db)):
    key_hash = get_hash(key)
    data = b''
    async for chunk in request.stream():
        data += chunk
    # TODO: Will have done
    create_or_update_data_item(db, key_hash, data)

    return Response(status_code=201)
