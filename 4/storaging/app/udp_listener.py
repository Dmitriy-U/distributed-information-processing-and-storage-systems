import json
import asyncio

from threading import Thread, Event
from sqlalchemy.orm import Session

from .logger import logger
from .helpers import get_hash
from .crud import create_node_if_not_exist


class UDPProtocol(asyncio.BaseProtocol):
    def __init__(self, app_key: str, db_session: Session):
        self._app_key = app_key
        self.transport = None
        self.db_session = db_session

    def connection_made(self, transport):
        self.transport = transport

    def datagram_received(self, data, addr: tuple):
        message = data.decode()
        data = json.loads(message)

        logger.info(f'receive udp packet --> {str(addr)} {str(data)}')

        key: int | None = data.get('key', None)
        if key is None or key != self._app_key:
            return

        ip: int | None = data.get('ip', None)
        if ip is None:
            return

        ip_address, port = addr

        # Сохранение текущей ноды
        with self.db_session() as session:
            logger.info(f"{ip_address} {ip}")
            # TODO: Получать ip-адрес из адреса отправителя
            create_node_if_not_exist(session, ip, get_hash(ip.encode()))


class UDPListenerTasks(Thread):
    def __init__(self, app_key: str, host: tuple[str, int], db_session: Session, *args, **kwargs):
        super(UDPListenerTasks, self).__init__(*args, **kwargs)

        self._host = host
        self._app_key = app_key
        self._stop_event = Event()
        self._loop = None
        self._transport = None
        self.db_session = db_session

    def run(self, *args, **kwargs):
        self._loop = asyncio.new_event_loop()
        listen = self._loop.create_datagram_endpoint(
            lambda: UDPProtocol(db_session=self.db_session, app_key=self._app_key),
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
