import argparse
import zmq

from enum import Enum

from constants import EXTERNAL_NODE_COUNT, FILE_SYSTEM


class Command(Enum):
    RUN = 'run'
    HAS = 'has'
    READ = 'read'
    WRITE = 'write'
    DELETE = 'delete'
    CHANGE_BLOCK = 'changeblock'

    @classmethod
    def list(cls) -> str:
        return list(map(lambda c: c.value, cls))


def parse_args() -> tuple[Command, None | str, None | str, None | int, None | bytes]:
    parser = argparse.ArgumentParser(prog="main.py", description="Распределённая файловая система")
    parser.add_argument('command', help='команда', choices=Command.list())
    parser.add_argument('--file', '-F', metavar="path", help="файл", type=str)
    parser.add_argument('--file_source', '-FS', metavar="path", help="файл записываемый", type=open)
    parser.add_argument('--block', '-B', metavar="NUMBER", help='номер блока', type=int)
    parser.add_argument('--block_data', '-BD', metavar="BLOB", help='данные блока', type=str)
    args = parser.parse_args()

    command = args.command
    file: None | str = args.file
    file_source: None | str = args.file_source
    block: None | int = args.block
    block_data: None | bytes = args.block_data

    return (command, file, file_source, block, block_data, )



def has_handler(fs: dict[str,dict[str,bytes]], file: None | str) -> bool:
    assert file is not None, "Вы не указали аргумент --file"

    return file in fs


def read_handler(fs: dict[str,dict[str,bytes]], file: None | str) -> dict[str,bytes]:
    assert file is not None, "Вы не указали аргумент --file"
    assert file in fs, f"Файл {file} отсутствует"

    return fs[file]


def handle_command(command, file, file_source, block, block_data):
    context = zmq.Context()

    receiver = context.socket(zmq.PULL)
    receiver.bind("tcp://127.0.0.255:9100")

    sender = context.socket(zmq.PUSH)
    sender.connect("tcp://127.0.0.255:9000")

    match command:
        case Command.HAS.value:
            try:
                has_file = has_handler(FILE_SYSTEM, file)
            except AssertionError as e:
                print(e)
                exit(0)

            if has_file:
                print(f"Файл {file} присутствует")
                exit(1)
            else:
                request = f"has:{file}"
                sender.send_string(request)

                has_external_file = False
                i = 0
                while not has_external_file and i < EXTERNAL_NODE_COUNT:
                    response = receiver.recv().decode('utf8')
                    if response.find(request) > -1:
                        has_external_file = bool(int(response.split(":").pop()))
                        i += 1

                print(f"Файл {file} присутствует" if has_external_file else f"Файл {file} отсутствует")
        case Command.READ.value:
            try:
                _, message = read_handler(FILE_SYSTEM, file)
                print(message)
            except AssertionError as e:
                print(e)
        case Command.WRITE.value:
            print("WRITE")
        case Command.DELETE.value:
            print("DELETE")
        case Command.CHANGE_BLOCK.value:
            print("CHANGE_BLOCK")
        case _:
            print("Команда отсутствует")
            exit(0)


def run_storage():
    print('Хранение запущено')

    context = zmq.Context()

    receiver = context.socket(zmq.PULL)
    receiver.bind("tcp://127.0.0.255:9000")

    sender = context.socket(zmq.PUSH)
    sender.connect("tcp://127.0.0.255:9100")

    while True:
        request = receiver.recv().decode('utf8')
        data = request.split(":")
        command, file = data

        match command:
            case Command.HAS.value:
                has_file = has_handler(FILE_SYSTEM, file)
                sender.send_string(f"{request}:{int(has_file)}")
            case Command.READ.value:
                print("READ")
            case Command.WRITE.value:
                print("WRITE")
            case Command.DELETE.value:
                print("DELETE")
            case Command.CHANGE_BLOCK.value:
                print("CHANGE_BLOCK")
            case _:
                print("Команда отсутствует")
                exit(0)
