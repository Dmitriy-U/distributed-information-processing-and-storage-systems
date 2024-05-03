import time
import socket

from threading import Thread

from constants import FILE_SYSTEM
from helpers import Command, fs_read, parse_args_storaging
from type import FileSystemFilePathName

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

(host, port) = parse_args_storaging()

s.bind((host, port))
s.listen(5)


def socket_handle(client_socket: socket.SocketType, client_addres: tuple[str, str]):
    while True:
        request_data = client_socket.recv(2048).decode("UTF-8")
        request_attr_list = request_data.split(":")

        print(request_attr_list, request_attr_list[0], Command.READ.value)
        match request_attr_list[0]:
            case Command.READ.value:
                file = request_attr_list[1]
                file_blocks = fs_read(FILE_SYSTEM, file) # type: ignore

                if file_blocks is None:
                    return

                file_block_id = f"{request_attr_list[2]}:{request_attr_list[3]}"
                
                if file_block_id not in file_blocks:
                    return

                block_data = file_blocks[file_block_id]
                data = block_data.decode("utf-8")
                response_data = f"{request_data}:{data}"

                if client_socket.send(bytes(response_data, 'UTF-8')) == len(response_data):
                    print("sent ", repr(response_data), " successfully.")
            case Command.WRITE.value:
                print("WRITE")
            case Command.DELETE.value:
                print("DELETE")
            case Command.CHANGE_BLOCK.value:
                print("CHANGE_BLOCK")
            case _:
                print("Команда отсутствует")
                exit(0)

        time.sleep(0.001)


while True:
    print(f"Хранение данных запущено по адресу {host}:{port}")
    c_socket, c_addres = s.accept()
    thread = Thread(target=socket_handle, args=(c_socket, c_addres))
    thread.start()
    time.sleep(0.001)
