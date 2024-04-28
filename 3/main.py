import zmq
import argparse

from enum import Enum

from helpers import has_handler, read_handler

fs: dict[str, dict[str, bytes]] = {
    "/test.txt": {
        "2:1": b"0xff",
        "2:2": b"0x00"
    }
}

HOST = "127.0.0.255"
PORT = 9999
BYTE_BLOCK_LENGTH = 1024
EXTERNAL_NODE_COUNT = 1


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

if command == Command.RUN.value:
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
                has_file, _ = has_handler(fs, file)
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
else:
    context = zmq.Context()

    receiver = context.socket(zmq.PULL)
    receiver.bind("tcp://127.0.0.255:9100")

    sender = context.socket(zmq.PUSH)
    sender.connect("tcp://127.0.0.255:9000")

    result: str | None = None

    match command:
        case Command.HAS.value:
            try:
                has_file, message = has_handler(fs, file)
            except AssertionError as e:
                print(e)
                exit(0)

            if has_file:
                request = f"has:{file}"
                sender.send_string(request)

                has_external_file = False
                i = 0
                while not has_external_file and i < EXTERNAL_NODE_COUNT:
                    response = receiver.recv().decode('utf8')
                    # TODO
                    print(response, request, response.find(request))
                    if response.find(request):
                        data = response.split(":")[-1:]

                        print('Has result: ', data)
                        print('Sended -->')
                        i += 1

            print(message)
        case Command.READ.value:
            try:
                _, message = read_handler(fs, file)
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
