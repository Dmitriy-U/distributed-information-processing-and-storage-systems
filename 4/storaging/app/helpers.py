import hashlib
import socket

from humps import camel


def get_self_ip_address(remote_server="google.com") -> str:
    """
    Получение собственного IP-адреса
    remote_server: с помощью этого сервера мы узнаем свой адрес в ответе
    """

    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        s.connect((remote_server, 80))
        return s.getsockname()[0]


def get_hash(string: bytes, hash_bit=8) -> int:
    """
    Получение хеша (по-умолчанию 8-битного)

    string: fsdf
    """

    return int(hashlib.sha1(string).hexdigest()[-int(hash_bit / 4):], 16)


def to_camel_case(string):
    return camel.case(string)
