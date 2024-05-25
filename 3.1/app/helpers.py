import json
import random
import requests
import argparse

from enum import Enum
from io import TextIOWrapper
from functools import reduce
from sqlalchemy.orm import Session

from app.crud import db_bulk_insert_blocks, db_insert_file_if_not_exist, db_insert_storage_if_not_exist
from app.models import Block
from app.constants import BYTE_BLOCK_LENGTH


def get_config() -> dict:
    with open('app/config.json', 'r') as f:
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
            block_count, _ = str(block.id).split(":")
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


def storage_change_file_block(block: Block, block_data: bytes) -> bool:
    try:
        response = requests.put(f'http://{block.storage_address}/{block.file_path_name}/{block.id}', block_data)
    except requests.exceptions.ConnectionError as e:
        return False

    return True


def write_file(session: Session, file_path_name: str, file_source: TextIOWrapper, host_list: list[str]) -> bool:
    with file_source as file:
        file_source_string = file.read(2048).encode()
        block_list = [file_source_string[start:start + BYTE_BLOCK_LENGTH] for start in
                      range(0, len(file_source_string), BYTE_BLOCK_LENGTH)]

    block_count = len(block_list)
    db_block_list: list[Block] = []
    for index, block in enumerate(block_list):
        host = random.choice(host_list)
        block_id = f"{block_count}:{index + 1}"
        response = requests.post(f'http://{host}/{file_path_name}/{block_id}', block)
        if response.status_code != 201:
            return False

        db_block_list.append(Block(id=block_id, file_path_name=file_path_name, storage_address=host))

    db_insert_file_if_not_exist(session, file_path_name)
    for storage_address in host_list:
        db_insert_storage_if_not_exist(session, storage_address)

    db_bulk_insert_blocks(session, db_block_list)

    return True


class Command(Enum):
    READ = 'read'
    WRITE = 'write'
    DELETE = 'delete'
    CHANGE_BLOCK = 'changeblock'

    @classmethod
    def list(cls) -> list:
        return list(map(lambda c: c.value, cls))


def parse_args_main() -> tuple[Command, None | str, None | TextIOWrapper, None | str, None | int, None | bytes]:
    parser = argparse.ArgumentParser(prog="main.py", description="Распределённая файловая система")
    parser.add_argument('--command', '-C', help='команда', choices=Command.list(), required=True)
    parser.add_argument('--file-path', '-F', metavar="path", help="файл", type=str)
    parser.add_argument('--input', '-I', metavar="path", help="файл источник", type=open)
    parser.add_argument('--output', '-O', metavar="path", help="файл для сохранения", type=str)
    parser.add_argument('--block-id', '-B', metavar="STRING", help='идентификатор блока (35:13)', type=str)
    parser.add_argument('--block-data', '-BD', metavar="BLOB", help='данные блока', type=str)
    args = parser.parse_args()

    command: Command = args.command
    file_path: None | str = args.file_path

    input: None | TextIOWrapper = args.input
    output: None | str = args.output
    block_id: None | int = args.block_id
    block_data: None | bytes = args.block_data

    return command, file_path, input, output, block_id, block_data


def parse_args_storaging() -> tuple[None | str, None | int]:
    parser = argparse.ArgumentParser(prog="storaging.py",
                                     description="Централизованная распределённая файловая система. Хранение данных")
    parser.add_argument('host', help='адрес хоста', type=str)
    parser.add_argument('port', help="порт", type=int)
    args = parser.parse_args()

    host: None | str = args.host
    port: None | int = args.port

    return host, port
