import argparse

from enum import Enum
from functools import reduce
from io import TextIOWrapper
import json
import socket

from constants import DB_PATH_NAME
from type import DataBase, DataBaseFile, DataBaseHost, FileSystem, FileSystemBlockId, FileSystemFilePathName


def get_config() -> dict:
    with open('config.json', 'r') as f:
        config_string = f.read()
    
    return json.loads(config_string)


def get_db() -> DataBase:
    with open(DB_PATH_NAME, 'r') as f:
        file_string = f.read()

    return json.loads(file_string)


def set_db(db: DataBase):
    with open(DB_PATH_NAME, 'w') as f:
        f.write(json.dumps(db))


def concatenate_bytes(x: bytes, y: bytes) -> bytes:
    return x + y


def has_file_in_db(db: DataBase, file: str) -> bool:
    return file in db


def get_file_data(file: str, db_file: DataBaseFile) -> bytes:
    db_host_list = db_file.keys()
    result_blocks: dict[str | int,bytes] = {}
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
            result_blocks[db_file_block_number] = bytes(response_data_items.pop().encode("utf-8")) # type: ignore
        s.close()

    block_items = list(dict(sorted(result_blocks.items())).values())
    
    assert len(block_items) != db_file_block_count, f"Отстутствуют блоки файлов"

    return reduce(concatenate_bytes, block_items)


class Command(Enum):
    HAS = 'has'
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

    command = args.command
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


def fs_has(fs: FileSystem, file: FileSystemFilePathName) -> bool:
    return file in fs


def fs_read(fs: FileSystem, file: FileSystemFilePathName) -> dict[FileSystemBlockId, bytes] | None:
    if fs_has(fs, file):
        return fs[file]
    else:
        return None
