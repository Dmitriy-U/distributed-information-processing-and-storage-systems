import argparse

from enum import Enum
from io import TextIOWrapper
import json

from constants import DB_PATH_NAME
from type import DataBase, DataBaseHost, FileSystem, FileSystemBlockId, FileSystemFilePathName


def get_db() -> DataBase:
    with open(DB_PATH_NAME, 'r') as f:
        file_string = f.read()

    return json.loads(file_string)


def set_db(db: DataBase):
    with open(DB_PATH_NAME, 'w') as f:
        f.write(json.dumps(db))


class Command(Enum):
    HAS = 'has'
    READ = 'read'
    WRITE = 'write'
    DELETE = 'delete'
    CHANGE_BLOCK = 'changeblock'

    @classmethod
    def list(cls) -> list:
        return list(map(lambda c: c.value, cls))


def parse_args_main() -> tuple[Command, set[DataBaseHost] | None, None | str, None | TextIOWrapper, None | int, None | bytes]:
    parser = argparse.ArgumentParser(prog="main.py", description="Распределённая файловая система")
    parser.add_argument('--command', '-C', help='команда', choices=Command.list(), required=True)
    parser.add_argument('--file', '-F', metavar="path", help="файл", type=str)
    parser.add_argument('--file-source', '-FS', metavar="path", help="файл записываемый", type=open)
    parser.add_argument('--block', '-B', metavar="NUMBER", help='номер блока', type=int)
    parser.add_argument('--block-data', '-BD', metavar="BLOB", help='данные блока', type=str)
    parser.add_argument('--host-list', '-HL', nargs='+', metavar="HOST", help='<Required> Set flag', type=DataBaseHost)
    args = parser.parse_args()

    command = args.command
    _host_list: list[DataBaseHost] | None = args.host_list
    if _host_list is None:
        host_list = _host_list
    else:
        host_list = set(_host_list)
    file: None | str = args.file
    file_source: None | TextIOWrapper = args.file_source
    block: None | int = args.block
    block_data: None | bytes = args.block_data

    return command, host_list, file, file_source, block, block_data


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
