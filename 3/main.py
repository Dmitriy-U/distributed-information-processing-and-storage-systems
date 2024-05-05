from functools import reduce
import random
import socket

from constants import BYTE_BLOCK_LENGTH
from helpers import Command, get_config, get_file_data, has_file_in_db, parse_args_main, get_db


def main():
    (command, file, file_source, block, block_data) = parse_args_main()

    match command:
        case Command.HAS.value:
            assert file is not None, "Вы не указали атрибут --file"
            
            has_file = has_file_in_db(get_db(), file)

            print(f"Файл {file} присутствует" if has_file else f"Файл {file} отсутствует")
        case Command.READ.value:
            assert file is not None, "Вы не указали атрибут --file"

            db_file = get_db().get(file) # type: ignore
            
            assert db_file is not None, f"Файл {file} отсутствует"
            
            file_data = get_file_data(file, db_file)
            
            print(f"Файл {file} {file_data}")
        case Command.WRITE.value:
            assert file is not None, "Вы не указали атрибут --file"
            assert file_source is not None, "Вы не указали атрибут --file-source"
            
            config = get_config()
            host_list: list[str] = config.get('hostList', None)
            
            print(host_list)
            
            assert host_list is not None, "Вы не указали атрибут --host-list"

            host_sockets: dict[str,socket.SocketType] = {}
            for host in host_list:
                address, port = host.split(":")

                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

                try:
                    s.connect((address, int(port)))
                    host_sockets[host] = s
                except BlockingIOError as e:
                    print("Ошибка подключения")
            
            print(host_sockets)

            with file_source as f:
                file_source_string = f.read(2048)
                block_list = [file_source_string[start:start + BYTE_BLOCK_LENGTH] for start in range(0, len(file_source_string), BYTE_BLOCK_LENGTH)]

            block_count = len(block_list)
            for index, block in enumerate(block_list):
                print(random.choice(host_list), index + 1, block_count, block)
                # TODO
            
            for sock in host_sockets.values():
                sock.close()

        case Command.DELETE.value:
            print("DELETE")
        case Command.CHANGE_BLOCK.value:
            print("CHANGE_BLOCK")
        case _:
            print("Команда отсутствует")
            exit(0)


if __name__ == "__main__":
    main()
