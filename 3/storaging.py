import time
import socket

from threading import Thread

from constants import FILE_SYSTEM
from helpers import Command, fs_has, fs_read

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

host = "127.0.0.255"
port = 1234

s.bind((host, port))
s.listen(5)


def socket_handle(client_socket: socket.SocketType, client_addres: tuple[str, str]):
    while True:
        request_data = client_socket.recv(2048).decode("UTF-8")
        request_attr_list = request_data.split(":")
        
        match request_attr_list[0]:
            case Command.HAS.value:
                _, file = request_attr_list
                has_file = fs_has(FILE_SYSTEM, file)
                response_data = f"{request_data}:{int(has_file)}"

                if client_socket.send(bytes(response_data, 'UTF-8')) == len(response_data):
                    print("sent ", repr(response_data), " successfully.")
            case Command.READ.value:
                _, file = request_attr_list
                file_blocks = fs_read(FILE_SYSTEM, file)

                if file_blocks is None:
                    return
                
                for block, block_data in file_blocks.items():
                    response_data = f"{request_data}:{block}:{block_data.decode("utf-8")}"

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
    c_socket, c_addres = s.accept()
    thread = Thread(target=socket_handle, args=(c_socket, c_addres))
    thread.start()
    time.sleep(0.001)
