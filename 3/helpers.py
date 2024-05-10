import argparse

from enum import Enum
from functools import reduce
from io import TextIOWrapper
import json
import random
import socket
import time

from constants import BYTE_BLOCK_LENGTH, DB_PATH_NAME
from type import DataBase, DataBaseBlockId, DataBaseFile, DataBaseFilePathName, DataBaseHost, FileSystem, FileSystemBlockId, FileSystemFilePathName


def get_config() -> dict:
    with open('config.json', 'r') as f:
        config_string = f.read()
    
    return json.loads(config_string)


def get_db() -> DataBase:
    with open(DB_PATH_NAME, 'r') as f:
        file_string = f.read()

    return DataBase(json.loads(file_string))


def set_db(db: DataBase):
    with open(DB_PATH_NAME, 'w') as f:
        f.write(json.dumps(db))


def concatenate_bytes(x: bytes, y: bytes) -> bytes:
    return x + y


def has_file_in_db(db: DataBase, file: str) -> bool:
    return file in db


def get_file_data(file: str, db_file: DataBaseFile) -> bytes:
    db_host_list = db_file.keys()
    result_blocks: dict[str | int, bytes] = {}
    db_file_block_count: None | int = None

    for db_host in db_host_list:
        host, port = db_host.split(":")
        db_block_id_list = db_file[db_host]

        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        try:
            s.connect((host, int(port)))
        except BlockingIOError as e:
            print("BlockingIOError")

        for db_block_id in db_block_id_list:
            db_file_block_count, db_file_block_number = map(lambda x: int(x), db_block_id.split(":"))

            if db_file_block_count is None:
                db_file_block_count = int(db_block_id.split(":")[0])
            request_data = f"{Command.READ.value}:{file}:{db_block_id}"

            s.send(bytes(request_data, 'UTF-8'))

            response_data = s.recv(2048).decode("UTF-8")
            response_data_items = response_data.split(":")
            result_blocks[db_file_block_number] = bytes(response_data_items.pop().encode("utf-8"))

        s.close()

    block_items = list(dict(sorted(result_blocks.items())).values())
    assert len(block_items) == db_file_block_count, f"Отстутствуют блоки файлов"

    return reduce(concatenate_bytes, block_items)


def delete_file(file: str, db_file: DataBaseFile) -> bool:
    db_host_list = db_file.keys()

    result = True
    for db_host in db_host_list:
        host, port = db_host.split(":")

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.connect((host, int(port)))
            except BlockingIOError as e:
                print("BlockingIOError")

            s.sendall(bytes(f"{Command.DELETE.value}:{file}", 'UTF-8'))
            
            response_data = s.recv(2048).decode("UTF-8")
    
        is_deleted = bool(int(response_data.split(":").pop()))
        if not is_deleted:
            result = False

    return result


def write_file(file: DataBaseFilePathName, file_source: TextIOWrapper, host_list: list[str]) -> DataBaseFile | None:
    host_sockets: dict[str,socket.SocketType] = {}
    for host in host_list:
        address, port = host.split(":")

        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        try:
            s.connect((address, int(port)))
            host_sockets[host] = s
        except BlockingIOError as e:
            print("Ошибка подключения")

    with file_source as f:
        file_source_string = f.read(2048)
        block_list = [file_source_string[start:start + BYTE_BLOCK_LENGTH] for start in range(0, len(file_source_string), BYTE_BLOCK_LENGTH)]

    block_count = len(block_list)
    db_file: DataBaseFile = DataBaseFile({})
    for index, block in enumerate(block_list):
        host = DataBaseHost(random.choice(host_list))
        block_id = DataBaseBlockId(f"{block_count}:{index + 1}")
        request_data = f"{Command.WRITE.value}:{file}:{block_id}:{block}"
        host_sockets[host].send(bytes(request_data, 'UTF-8'))
        
        response_data = s.recv(2048).decode("UTF-8")
        is_wrote = bool(int(response_data.split(":").pop()))
        
        if not is_wrote:
            break

        if host not in db_file:
            db_file[host] = []
        db_file[host].append(block_id)

    return db_file


class Command(Enum):
    HAS = 'has'
    READ = 'read'
    WRITE = 'write'
    DELETE = 'delete'
    CHANGE_BLOCK = 'changeblock'

    @classmethod
    def list(cls) -> list:
        return list(map(lambda c: c.value, cls))


def parse_args_main() -> tuple[Command, None | DataBaseFilePathName, None | TextIOWrapper, None | int, None | bytes]:
    parser = argparse.ArgumentParser(prog="main.py", description="Распределённая файловая система")
    parser.add_argument('--command', '-C', help='команда', choices=Command.list(), required=True)
    parser.add_argument('--file', '-F', metavar="path", help="файл", type=str)
    parser.add_argument('--file-source', '-FS', metavar="path", help="файл записываемый", type=open)
    parser.add_argument('--block', '-B', metavar="NUMBER", help='номер блока', type=int)
    parser.add_argument('--block-data', '-BD', metavar="BLOB", help='данные блока', type=str)
    args = parser.parse_args()

    command = args.command
    _file: None | str = args.file
    if _file is None:
        file = None
    else:
        file = DataBaseFilePathName(_file)
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


def fs_has(fs: FileSystem, file: FileSystemFilePathName) -> bool:
    return file in fs


def fs_delete_file(fs: FileSystem, file: FileSystemFilePathName) -> bool:
    if file in fs:
        del fs[file]
        return True
    else:
        return False


def fs_read_file_blocks(fs: FileSystem, file: FileSystemFilePathName) -> dict[FileSystemBlockId, bytes] | None:
    if fs_has(fs, file):
        return fs[file]
    else:
        return None


def fs_read_file_block(fs: FileSystem, file: FileSystemFilePathName, file_block_id: FileSystemBlockId) -> bytes | None:
    file_blocks = fs_read_file_blocks(fs, file)
    if (file_blocks is not None) and (file_block_id in file_blocks):
        return file_blocks[file_block_id]
    else:
        return None


def fs_write_file_block(fs: FileSystem, file: FileSystemFilePathName,
                        file_block_id: FileSystemBlockId, file_block_data: bytes) -> bool:
    if file not in fs:
        fs[file] = {}

    fs[file][file_block_id] = file_block_data
    return True
