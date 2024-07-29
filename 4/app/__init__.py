import requests

from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from sqlalchemy.orm import Session

from .constants import UDP_PORT, APP_KEY, IP_ADDRESS_BROADCAST, HASH_BIT_MAX_VALUE, TCP_PORT, \
    ADVERTISE_PERIODIC_CALL_SECONDS
from .database import SessionLocal, Base, engine, get_db
from .crud import create_node_if_not_exist, create_or_update_data_item, get_nodes, delete_data_item, get_data_item
from .helpers import get_self_ip_address, get_hash, to_camel_case, search_before_and_after_nodes, make_advertise
from .logger import logger
from .periodic_call_handler import PeriodicCallHandler
from .responses import OctetStreamResponse, RawResponse
from .schemas import NodeRequestData
from .udp_listener import UDPNodeSynchronizationLoop

advertise_listener_thread = UDPNodeSynchronizationLoop(
    app_key=APP_KEY,
    host=(IP_ADDRESS_BROADCAST, UDP_PORT),
    ip_address_self=get_self_ip_address()
)

make_advertise_periodic = PeriodicCallHandler(lambda: make_advertise(), ADVERTISE_PERIODIC_CALL_SECONDS)


@asynccontextmanager
async def lifespan(app):
    logger.info('sub startup')
    ip_address = get_self_ip_address()
    ip_address_hash = get_hash(ip_address.encode())
    logger.info(f"Собственный ip адрес: {ip_address}")
    logger.info(f"Собственный hash ip адреса: {ip_address_hash}")

    # Сохранение текущей ноды
    with SessionLocal() as session:
        create_node_if_not_exist(session, ip_address, get_hash(ip_address.encode()))

    # Отправка информации о себе
    make_advertise()

    # Запуск прослушивания
    advertise_listener_thread.start()
    logger.info("Запущено прослушивание порта синхронизации")

    await make_advertise_periodic.start()
    logger.info("Запущено прослушивание порта синхронизации")
    yield
    logger.info("sub shutdown")
    await make_advertise_periodic.stop()
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

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

Base.metadata.create_all(bind=engine)


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
    logger.info(f"node_hash_before: {node_hash_before}, node_hash_after: {node_hash_after}")

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
        logger.info(f"GET://{node_ip_address}:{TCP_PORT}/data/{key}")
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
    logger.info(f"node_hash_before: {node_hash_before}, node_hash_after: {node_hash_after}")

    node_ip_address = nodes.get(node_hash_before)
    node_ip_address_self = get_self_ip_address()

    logger.info(f"node_ip_address: {node_ip_address}, node_ip_address_self: {node_ip_address_self}")
    if node_ip_address == node_ip_address_self:
        create_or_update_data_item(db, key_hash, data)
    else:
        logger.info(f"POST://{node_ip_address}:{TCP_PORT}/data/{key}")
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
    logger.info(f"node_hash_before: {node_hash_before}, node_hash_after: {node_hash_after}")

    node_ip_address = nodes.get(node_hash_before)
    node_ip_address_self = get_self_ip_address()

    logger.info(f"node_ip_address: {node_ip_address}, node_ip_address_self: {node_ip_address_self}")
    if node_ip_address == node_ip_address_self:
        delete_data_item(db, key_hash)
    else:
        logger.info(f"DELETE://{node_ip_address}:{TCP_PORT}/data/{key}")
        requests.delete(f'http://{node_ip_address}:{TCP_PORT}/data/{key}')
