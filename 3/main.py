import time
import socket
import select

from constants import BYTE_BLOCK_LENGTH, EXTERNAL_NODE_COUNT, FILE_SYSTEM
from helpers import Command, parse_args, fs_read

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

host = "127.0.0.255"
port = 1234


if __name__ == "__main__":
    (command, file, file_source, block, block_data) = parse_args()
    
    try:
        s.connect((host, port))
    except BlockingIOError as e:
        print("BlockingIOError")

    match command:
        case Command.HAS.value:
            assert file is not None, "Вы не указали атрибут --file"

            request_data = f"{Command.HAS.value}:{file}"

            select.select([], [s], [])
            if s.send(bytes(request_data, 'UTF-8')) == len(request_data):
                print("sent ", repr(request_data), " successfully.")

            has_file: bool = False
            i = 0
            while has_file is False and i < EXTERNAL_NODE_COUNT:
                response_data = s.recv(2048).decode("UTF-8")
                has_file = bool(int(response_data.split(":")[-1]))
                i += 1
                time.sleep(0.001)

            print(f"Файл {file} присутствует" if has_file else f"Файл {file} отсутствует")
        case Command.READ.value:
            assert file is not None, "Вы не указали атрибут --file"

            request_data = f"{Command.READ.value}:{file}"
            
            select.select([], [s], [])
            if s.send(bytes(request_data, 'UTF-8')) == len(request_data):
                print("sent ", repr(request_data), " successfully.")

            i = 0
            while True:
                response_data = s.recv(2048).decode("UTF-8")
                response_data_items = response_data.split(":")
                print(response_data_items, sep="\n")
                i += 1
                time.sleep(0.001)
                # TODO

        case Command.WRITE.value:
            assert file is not None, "Вы не указали атрибут --file"
            assert file_source is not None, "Вы не указали атрибут --file_source"

            with file_source as f:
                file_source_string = f.read(1024)
                file_parts = [file_source_string[start:start + BYTE_BLOCK_LENGTH] for start in range(0, len(file_source_string), BYTE_BLOCK_LENGTH)]
                print(file_parts)
                # TODO
            
        case Command.DELETE.value:
            print("DELETE")
        case Command.CHANGE_BLOCK.value:
            print("CHANGE_BLOCK")
        case _:
            print("Команда отсутствует")
            exit(0)
