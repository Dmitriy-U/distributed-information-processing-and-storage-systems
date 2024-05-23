import argparse

from enum import Enum
from functools import reduce
from io import TextIOWrapper
import json
import random
import socket
import requests

from app.models import Block

from .constants import BYTE_BLOCK_LENGTH


def get_config() -> dict:
    with open('config.json', 'r') as f:
        config_string = f.read()
    
    return json.loads(config_string)


def _concatenate_bytes(x: bytes, y: bytes) -> bytes:
    return x + y


def get_file_data(block_list: list[Block]) -> bytes:
    result_blocks: dict[str | int, bytes] = {}
    file_block_count: None | int = None

    for block in block_list:
        host, port = str(block.storage_address).split(":")
        
        if file_block_count is None:
            block_count, _ =str(block.id).split(":")
            file_block_count = int(block_count)

        response = requests.get(f'http://{host}:{port}/{block.file_path_name}/{block.id}')
        
        result_blocks[block.id] = response.content

    block_items = list(dict(sorted(result_blocks.items())).values())
    assert len(block_items) == file_block_count, f"Отстутствуют блоки файлов"

    return reduce(_concatenate_bytes, block_items)


def storage_delete_file(file_path_name: str, storage_addresses: set[str]) -> bool:
    try:
        for storage_address in storage_addresses:
            requests.delete(f'http://{storage_address}/{file_path_name}')
    except requests.exceptions.ConnectionError as e:
        return False

    return True


# def write_file(file: DataBaseFilePathName, file_source: TextIOWrapper, host_list: list[str]) -> DataBaseFile | None:
#     host_sockets: dict[str,socket.SocketType] = {}
#     for host in host_list:
#         address, port = host.split(":")

#         s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

#         try:
#             s.connect((address, int(port)))
#             host_sockets[host] = s
#         except BlockingIOError as e:
#             print("Ошибка подключения")

#     with file_source as f:
#         file_source_string = f.read(2048)
#         block_list = [file_source_string[start:start + BYTE_BLOCK_LENGTH] for start in range(0, len(file_source_string), BYTE_BLOCK_LENGTH)]

#     block_count = len(block_list)
#     db_file: DataBaseFile = DataBaseFile({})
#     for index, block in enumerate(block_list):
#         host = DataBaseHost(random.choice(host_list))
#         block_id = DataBaseBlockId(f"{block_count}:{index + 1}")
#         request_data = f"{Command.WRITE.value}:{file}:{block_id}:{block}"
#         host_sockets[host].send(bytes(request_data, 'UTF-8'))
        
#         response_data = s.recv(2048).decode("UTF-8")
#         is_wrote = bool(int(response_data.split(":").pop()))
        
#         if not is_wrote:
#             break

#         if host not in db_file:
#             db_file[host] = []
#         db_file[host].append(block_id)

#     return db_file


# def change_block_file(db_file: DataBaseFile, file: DataBaseFilePathName, block: int, block_data: bytes) -> bool:
#     block_changed = False
#     for host in db_file:
#         print(host)
#         for block_id in db_file[host]:
#             _, block_local = block_id.split(":")
#             block_local = int(block_local)
#             if block == block_local:
                
#                 address, port = host.split(":")

#                 s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

#                 try:
#                     s.connect((address, int(port)))
#                 except BlockingIOError as e:
#                     print("Ошибка подключения")
                
#                 request_data = f"{Command.CHANGE_BLOCK.value}:{file}:{block_local}:{block_data}"
#                 s.send(bytes(request_data, 'UTF-8'))
                
#                 response_data = s.recv(2048).decode("UTF-8")
#                 block_changed = bool(int(response_data.split(":").pop()))
#                 break

#     return block_changed


class Command(Enum):
    READ = 'read'
    WRITE = 'write'
    DELETE = 'delete'
    CHANGE_BLOCK = 'changeblock'

    @classmethod
    def list(cls) -> list:
        return list(map(lambda c: c.value, cls))


def parse_args_main() -> tuple[Command, None | str, None | TextIOWrapper, None | int, None | bytes]:
    parser = argparse.ArgumentParser(prog="main.py", description="Распределённая файловая система")
    parser.add_argument('--command', '-C', help='команда', choices=Command.list(), required=True)
    parser.add_argument('--file', '-F', metavar="path", help="файл", type=str)
    parser.add_argument('--file-source', '-FS', metavar="path", help="файл записываемый", type=open)
    parser.add_argument('--block', '-B', metavar="NUMBER", help='номер блока', type=int)
    parser.add_argument('--block-data', '-BD', metavar="BLOB", help='данные блока', type=str)
    args = parser.parse_args()

    command: Command = args.command
    file: None | str = args.file

    file_source: None | TextIOWrapper = args.file_source
    block: None | int = args.block
    block_data: None | bytes = args.block_data

    return command, file, file_source, block, block_data


def parse_args_storaging() -> tuple[None | str, None | int]:
    parser = argparse.ArgumentParser(prog="storaging.py",
                                     description="Централизованная распределённая файловая система. Хранение данных")
    parser.add_argument('host', help='адрес хоста', type=str)
    parser.add_argument('port', help="порт", type=int)
    args = parser.parse_args()

    host: None | str = args.host
    port: None | int = args.port

    return host, port


# def fs_has(fs: FileSystem, file: FileSystemFilePathName) -> bool:
#     return file in fs


# def fs_delete_file(fs: FileSystem, file: FileSystemFilePathName) -> bool:
#     if file in fs:
#         del fs[file]
#         return True
#     else:
#         return False


# def fs_read_file_blocks(fs: FileSystem, file: FileSystemFilePathName) -> dict[FileSystemBlockId, bytes] | None:
#     if fs_has(fs, file):
#         return fs[file]
#     else:
#         return None


# def fs_read_file_block(cur: Cursor, file: FileSystemFilePathName, file_block_id: FileSystemBlockId) -> bytes | None:
#     res = cur.execute(f'SELECT data FROM blocks WHERE file = "{file}" AND block = "{file_block_id}"')
#     result: None | tuple[bytes] = res.fetchone()
#     print('result', result)
#     if result is None:
#         return None
#     else:
#         return result[0]


# def fs_write_file_block(cur: Cursor, file: FileSystemFilePathName,
#                         file_block_id: FileSystemBlockId, file_block_data: bytes) -> bool:
#     res = cur.execute(f'INSERT INTO files (file_path) VALUES("{file}")')
#     res = cur.execute(f'INSERT INTO blocks (block, file, data) VALUES("{file_block_id}", "{file}", "{file_block_data}")')
#     result = res.fetchall()
#     print('result', result)

#     return True


# def fs_write_file_block_by_block_number(fs: FileSystem, file: FileSystemFilePathName,
#                         file_block_number: int, file_block_data: bytes) -> bool:
#     if file not in fs:
#         return False
    
#     result = False
#     for file_block_id in fs[file].keys():
#         print(file_block_id)
#         _, block_number = file_block_id.split(":")
#         if int(block_number) == file_block_number:
#             fs[file][file_block_id] = file_block_data
#             result = True
#             break

#     return result
