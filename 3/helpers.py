import argparse
import sqlite3

from enum import Enum
from io import TextIOWrapper

from constants import DB_PATH_NAME


def get_db_connection() -> sqlite3.Connection:
    return sqlite3.connect(DB_PATH_NAME)


def db_prepare(db_connection: sqlite3.Connection):
    cur = db_connection.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS hosts (
          host VARCHAR(10) NOT NULL
        );
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS files (
            file VARCHAR(256) NOT NULL,
            PRIMARY KEY (file),
            FOREIGN KEY (file) REFERENCES hosts(host)
        );
    """)

    db_connection.commit()


class Command(Enum):
    HAS = 'has'
    READ = 'read'
    WRITE = 'write'
    DELETE = 'delete'
    CHANGE_BLOCK = 'changeblock'

    @classmethod
    def list(cls) -> list:
        return list(map(lambda c: c.value, cls))


def parse_args_main() -> tuple[Command, list[str], None | str, None | TextIOWrapper, None | int, None | bytes]:
    parser = argparse.ArgumentParser(prog="main.py", description="Распределённая файловая система")
    parser.add_argument('--command', '-C', help='команда', choices=Command.list(), required=True)
    parser.add_argument('--file', '-F', metavar="path", help="файл", type=str)
    parser.add_argument('--file-source', '-FS', metavar="path", help="файл записываемый", type=open)
    parser.add_argument('--block', '-B', metavar="NUMBER", help='номер блока', type=int)
    parser.add_argument('--block-data', '-BD', metavar="BLOB", help='данные блока', type=str)
    parser.add_argument('--host-list', '-HL', nargs='+', metavar="HOST", help='<Required> Set flag', type=str,
                        required=True)
    args = parser.parse_args()

    command = args.command
    host_list: list[str] = args.host_list
    file: None | str = args.file
    file_source: None | TextIOWrapper = args.file_source
    block: None | int = args.block
    block_data: None | bytes = args.block_data

    print(host_list)

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


def fs_has(fs: dict[str, dict[str, bytes]], file: str) -> bool:
    return file in fs


def fs_read(fs: dict[str, dict[str, bytes]], file: str) -> dict[str, bytes] | None:
    if fs_has(fs, file):
        return fs[file]
    else:
        return None
