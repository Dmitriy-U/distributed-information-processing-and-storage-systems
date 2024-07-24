import hashlib
import socket

from humps import camel

from .constants import HASH_BIT_COUNT


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
