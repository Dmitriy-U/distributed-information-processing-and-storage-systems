import hashlib
import socket
import json

from humps import camel

from .logger import logger
from .constants import HASH_BIT_COUNT, IP_ADDRESS_BROADCAST, UDP_PORT, APP_KEY


def get_self_ip_address() -> str:
    """Получение собственного IP-адреса"""

    hostname = socket.gethostname()
    ip_address = socket.gethostbyname(hostname)

    return ip_address


def get_hash(string: bytes, hash_bit=HASH_BIT_COUNT) -> int:
    """
    Получение хеша (по-умолчанию 8-битного)

    string: fsdf
    """

    return int(hashlib.sha1(string).hexdigest()[-int(hash_bit / 4):], 16)


def to_camel_case(string):
    return camel.case(string)


def search_before_and_after_nodes(target_hash: int, node_hash_list: list[int]):
    """
    Поиск предыдущего и следующего хешей по модулю относительно целевого хеша среди списка хешей
    :param target_hash: необходимый хеш
    :param node_hash_list: список хешей
    :return: предыдущий и следующий хеши относительно целевого
    """

    node_hash_list_len = len(node_hash_list)

    if node_hash_list_len == 0:
        return None, None

    if node_hash_list_len == 1:
        node_hash_single = node_hash_list[0]
        return node_hash_single, node_hash_single

    node_hash_before, node_hash_after = None, None
    for index, node_hash in enumerate(node_hash_list):
        if target_hash >= node_hash:
            node_hash_before = node_hash
        else:
            node_hash_after = node_hash
            break

    if node_hash_before is None:
        node_hash_before = node_hash_list[-1]

    if node_hash_after is None:
        node_hash_after = node_hash_list[1]

    return node_hash_before, node_hash_after


def make_advertise():
    """Отправка информации о себе"""

    ip_address_self = get_self_ip_address()
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    advertise = {"ip": ip_address_self, "key": APP_KEY}
    sock.sendto(json.dumps(advertise).encode(), (IP_ADDRESS_BROADCAST, UDP_PORT))
    logger.info(f"Advertise: {ip_address_self}")
