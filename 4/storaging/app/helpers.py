import hashlib
import socket

from humps import camel


def get_self_ip_address(remote_server="google.com") -> str:
    """
    Return the/a network-facing IP number for this system.
    """
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        s.connect((remote_server, 80))
        return s.getsockname()[0]


def get_hash(string: bytes) -> int:
    return int(hashlib.sha1(string).hexdigest(), 16) % (10 ** 9)


def to_camel_case(string):
    return camel.case(string)
