import random
import socket

from constants import BYTE_BLOCK_LENGTH
from helpers import Command, delete_file, get_config, get_file_data, has_file_in_db, parse_args_main, get_db, set_db
from type import DataBaseBlockId, DataBaseFile, DataBaseHost


def main():
    (command, file, file_source, block, block_data) = parse_args_main()

    match command:
        case Command.HAS.value:
            assert file is not None, "Вы не указали атрибут --file"
            
            has_file = has_file_in_db(get_db(), file)

            print(f"Файл {file} присутствует" if has_file else f"Файл {file} отсутствует")
        case Command.READ.value:
            assert file is not None, "Вы не указали атрибут --file"

            db = get_db()
            db_file = db.get(file, None) # type: ignore
            
            assert db_file is not None, f"Файл {file} отсутствует"
            
            file_data = get_file_data(file, db_file)
            
            print(f"Файл {file} {file_data}")
        case Command.WRITE.value:
            assert file is not None, "Вы не указали атрибут --file"
            assert file_source is not None, "Вы не указали атрибут --file-source"
            
            config = get_config()
            host_list: list[str] = config.get('hostList', None)
            
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

            with file_source as f:
                file_source_string = f.read(2048)
                block_list = [file_source_string[start:start + BYTE_BLOCK_LENGTH] for start in range(0, len(file_source_string), BYTE_BLOCK_LENGTH)]

            block_count = len(block_list)
            db_file: DataBaseFile = DataBaseFile({})
            for index, block in enumerate(block_list):
                host = DataBaseHost(random.choice(host_list))
                block_id = DataBaseBlockId(f"{block_count}:{index + 1}")
                request_data = f"{Command.WRITE.value}:{file}:{block_id}:{block}"
                host_sockets[host].send(bytes(request_data, 'UTF-8'))

                if host not in db_file:
                    db_file[host] = []
                db_file[host].append(block_id)
            
            db = get_db()
            
            db[file] = db_file
            
            set_db(db)
        case Command.DELETE.value:
            assert file is not None, "Вы не указали атрибут --file"

            db = get_db()
            db_file = db.get(file, None) # type: ignore
            
            assert db_file is not None, f"Файл {file} отсутствует"
            
            is_deleted = delete_file(file, db_file)
            
            del db[file]
            set_db(db)
            
            print(f"Файл удалён" if is_deleted else f"Файл не был удалён")
        case Command.CHANGE_BLOCK.value:
            print("CHANGE_BLOCK")
        case _:
            print("Команда отсутствует")
            exit(0)


if __name__ == "__main__":
    main()
