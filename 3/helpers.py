import argparse

from enum import Enum
from io import TextIOWrapper

from constants import EXTERNAL_NODE_COUNT, FILE_SYSTEM, HOST, PORT_FROM_MAIN, PORT_FROM_STORAGE


class Command(Enum):
    HAS = 'has'
    READ = 'read'
    WRITE = 'write'
    DELETE = 'delete'
    CHANGE_BLOCK = 'changeblock'

    @classmethod
    def list(cls) -> list:
        return list(map(lambda c: c.value, cls))


def parse_args() -> tuple[Command, None | str, None | TextIOWrapper, None | int, None | bytes]:
    parser = argparse.ArgumentParser(prog="main.py", description="Распределённая файловая система")
    parser.add_argument('command', help='команда', choices=Command.list())
    parser.add_argument('--file', '-F', metavar="path", help="файл", type=str)
    parser.add_argument('--file-source', '-FS', metavar="path", help="файл записываемый", type=open)
    parser.add_argument('--block', '-B', metavar="NUMBER", help='номер блока', type=int)
    parser.add_argument('--block_data', '-BD', metavar="BLOB", help='данные блока', type=str)
    args = parser.parse_args()

    command = args.command
    file: None | str = args.file
    file_source: None | TextIOWrapper = args.file_source
    block: None | int = args.block
    block_data: None | bytes = args.block_data

    return (command, file, file_source, block, block_data, )



def fs_has(fs: dict[str,dict[str,bytes]], file: str) -> bool:
    return file in fs


def fs_read(fs: dict[str,dict[str,bytes]], file: str) -> dict[str,bytes] | None:
    if fs_has(fs, file):
        return fs[file]
    else:
        return None
