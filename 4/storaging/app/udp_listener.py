import json
import asyncio
import requests

from threading import Thread, Event

from .database import SessionLocal
from .logger import logger
from .helpers import get_hash
from .constants import APP_KEY, TCP_PORT
from .crud import create_node_if_not_exist, get_node_ip_list


class NodeSynchronizationHandleFactory(asyncio.BaseProtocol):
    def __init__(self, app_key: str):
        self._app_key = app_key
        self.transport = None

    def connection_made(self, transport):
        self.transport = transport

    def datagram_received(self, data, addr: tuple):
        message = data.decode()
        data = json.loads(message)

        logger.info(f'Receive udp packet --> {str(addr)} {str(data)}')

        key: int | None = data.get('key', None)
        if key is None or key != self._app_key:
            return

        ip: int | None = data.get('ip', None)
        if ip is None:
            return

        if key != APP_KEY:
            return

        ip_address, _ = addr

        with SessionLocal() as db_session:
            # Запись новой ноды
            logger.info(f"Create advertised node if not exist: {ip_address}")
            create_node_if_not_exist(db_session, ip_address, get_hash(ip_address.encode()))

            # Отправка известных нод
            ip_list = get_node_ip_list(db_session)
            requests.put(f'http://{ip_address}:{TCP_PORT}/nodes', json={"ipList": ip_list})


class UDPNodeSynchronizationLoop(Thread):
    def __init__(self, app_key: str, host: tuple[str, int], *args, **kwargs):
        super(UDPNodeSynchronizationLoop, self).__init__(*args, **kwargs)

        self._host = host
        self._app_key = app_key
        self._stop_event = Event()
        self._loop = None
        self._transport = None

    def run(self, *args, **kwargs):
        self._loop = asyncio.new_event_loop()
        listen = self._loop.create_datagram_endpoint(
            lambda: NodeSynchronizationHandleFactory(app_key=self._app_key),
            local_addr=self._host,
            allow_broadcast=True
        )
        transport, protocol = self._loop.run_until_complete(listen)

        self._transport = transport

        try:
            self._loop.run_forever()
        except KeyboardInterrupt:
            pass

        self._transport.close()
        self._loop.close()

    def stop(self):
        self._transport.close()
        self._loop.stop()
        self._loop.close()
        self._stop_event.set()
