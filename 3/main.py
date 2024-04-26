import zmq
import argparse

from enum import Enum


HOST = "127.0.0.255"
PORT = 9999

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
file = args.file
file_source = args.file_source
block = args.block
block_data = args.block_data

if command == Command.RUN.value:
    print('Хранение запущено')
    
    context = zmq.Context()

    receiver = context.socket(zmq.PULL)
    receiver.bind("tcp://*:9000")

    sender = context.socket(zmq.PUSH)
    sender.connect("tcp://127.0.0.255:9000")

    while True:
        data = receiver.recv()
        
        print('Has result: ', data.decode('utf8'))
        sender.send_string(data.decode('utf8'))
        print('Sended -->')
else:
    match command:
        case Command.HAS.value:
            print("HAS")
        case Command.READ.value:
            print("READ")
        case Command.WRITE.value:
            print("WRITE")
        case Command.DELETE.value:
            print("DELETE")
        case _:
            print("Команда отсутствует")
            exit(1)
