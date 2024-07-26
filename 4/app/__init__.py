import json
import socket

from contextlib import asynccontextmanager

import requests
from fastapi import FastAPI, Request, Depends
from fastapi.responses import Response
from sqlalchemy.orm import Session

from .constants import UDP_PORT, APP_KEY, IP_ADDRESS_BROADCAST, HASH_BIT_MAX_VALUE, TCP_PORT
from .database import SessionLocal, Base, engine, get_db
from .crud import create_node_if_not_exist, create_or_update_data_item, get_nodes, delete_data_item, get_data_item
from .helpers import get_self_ip_address, get_hash, to_camel_case, search_before_and_after_nodes
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


app = FastAPI(
    title="Лабораторная работа 4. Хранение данных",
    summary="Децентрализованное хранение данных",
    version="1.0.0",
    contact={"test": "test"},
    separate_input_output_schemas=False,
    lifespan=lifespan
)

Base.metadata.create_all(bind=engine)


class RawResponse(Response):
    media_type = "binary/octet-stream"

    def render(self, content: bytes) -> bytes:
        return bytes([b ^ 0x54 for b in content])


@app.put(
    "/nodes",
    tags=["Внутреннее API"],
    summary="Обновление нод",
    status_code=201
)
async def nodes_update(nodes: NodeRequestData, db: Session = Depends(get_db)):
    logger.info(f'Nodes update --> {nodes}')
    for ip in nodes.ip_list:
        create_node_if_not_exist(db, ip, get_hash(ip.encode()))


@app.get("/data/{key}", tags=["API"], response_class=OctetStreamResponse, status_code=200,
         summary="Получить данные ключа")
async def data_get(key: str, db: Session = Depends(get_db)):
    key_hash = get_hash(key.encode())
    logger.info(f'Get key --> {str(key_hash)}')

    node_list = get_nodes(db)

    nodes = {}
    for node in node_list:
        nodes[node.hash] = node.ip

    node_hash_before, node_hash_after = search_before_and_after_nodes(key_hash, list(nodes.keys()))

    node_ip_address = nodes.get(node_hash_before)
    node_ip_address_self = get_self_ip_address()

    binary_data: None | bytes
    if node_ip_address == node_ip_address_self:
        data_item = get_data_item(db, key_hash)
        if data_item is None:
            binary_data = None
        else:
            binary_data = data_item.data
    else:
        response = requests.get(f'http://{node_ip_address}:{TCP_PORT}/data/{key}', stream=True)
        if response.status_code == 200:
            binary_data = response.content
        else:
            binary_data = None

    if binary_data is None:
        return Response(status_code=404)
    else:
        return Response(
            binary_data,
            media_type="application/octet-stream",
        )


@app.post("/data/{key}", tags=["API"], status_code=201, summary="Записать данные ключа")
async def data_create(key: str, request: Request, db: Session = Depends(get_db)):
    key_hash = get_hash(key.encode())

    data = b''
    async for chunk in request.stream():
        data += chunk

    node_list = get_nodes(db)

    nodes = {}
    for node in node_list:
        nodes[node.hash] = node.ip

    node_hash_before, node_hash_after = search_before_and_after_nodes(key_hash, list(nodes.keys()))

    node_ip_address = nodes.get(node_hash_before)
    node_ip_address_self = get_self_ip_address()

    if node_ip_address == node_ip_address_self:
        create_or_update_data_item(db, key_hash, data)
    else:
        requests.post(f'http://{node_ip_address}:{TCP_PORT}/data/{key}', data=data)

    return Response(status_code=201)


@app.delete("/data/{key}", tags=["API"], status_code=200, summary="Удалить ключ")
async def keys_delete(key: str, db: Session = Depends(get_db)):
    key_hash = get_hash(key.encode())
    node_list = get_nodes(db)

    nodes = {}
    for node in node_list:
        nodes[node.hash] = node.ip

    node_hash_before, node_hash_after = search_before_and_after_nodes(key_hash, list(nodes.keys()))

    node_ip_address = nodes.get(node_hash_before)
    node_ip_address_self = get_self_ip_address()

    if node_ip_address == node_ip_address_self:
        delete_data_item(db, key_hash)
    else:
        requests.delete(f'http://{node_ip_address}:{TCP_PORT}/data/{key}')
