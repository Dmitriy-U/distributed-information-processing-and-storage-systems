import time
import socket

from threading import Thread

from constants import FILE_SYSTEM
from helpers import Command, fs_read_file_block, fs_write_file_block, parse_args_storaging
from type import FileSystemBlockId, FileSystemFilePathName

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

(host, port) = parse_args_storaging()

s.bind((host, port))
s.listen(5)


def socket_handle(client_socket: socket.SocketType, client_addres: tuple[str, str]):
    while True:
        request_data = client_socket.recv(2048).decode("UTF-8")
        request_attr_list = request_data.split(":")

        match request_attr_list[0]:
            case Command.READ.value:
                print('FILE_SYSTEM ->', FILE_SYSTEM)
                file = FileSystemFilePathName(request_attr_list[1]) # type: ignore
                file_block_id = FileSystemBlockId(f"{request_attr_list[2]}:{request_attr_list[3]}") # type: ignore
                file_block_data = fs_read_file_block(FILE_SYSTEM, file, file_block_id)

                assert file_block_data is not None, f"Блок {file_block_id} файла {file} отстутсвует"

                data = file_block_data.decode("utf-8")
                response_data = f"{request_data}:{data}"

                if client_socket.send(bytes(response_data, 'UTF-8')) == len(response_data):
                    print("sent ", repr(response_data), " successfully.")
                print(Command.READ.value, ' --> ', FILE_SYSTEM)
            case Command.WRITE.value:
                file = FileSystemFilePathName(request_attr_list[1]) # type: ignore
                file_block_id = FileSystemBlockId(f"{request_attr_list[2]}:{request_attr_list[3]}") # type: ignore
                file_block_data = bytes(request_attr_list[4], "UTF-8")
                
                fs_write_file_block(FILE_SYSTEM, file, file_block_id, file_block_data)
                print(Command.WRITE.value, ' --> ', FILE_SYSTEM)
            case Command.DELETE.value:
                print("DELETE", request_attr_list)
            case Command.CHANGE_BLOCK.value:
                print("CHANGE_BLOCK", request_attr_list)
            case _:
                print("Команда отсутствует", request_attr_list)

        time.sleep(0.001)


print(f"Хранение данных запущено по адресу {host}:{port}")
while True:
    c_socket, c_addres = s.accept()
    thread = Thread(target=socket_handle, args=(c_socket, c_addres))
    thread.start()
    time.sleep(0.001)
