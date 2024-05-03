from functools import reduce
import socket

from constants import BYTE_BLOCK_LENGTH
from helpers import Command, parse_args_main, get_db


def concatenate(x: bytes, y: bytes) -> bytes:
    return x + y

def main():
    (command, host_list, file, file_source, block, block_data) = parse_args_main()

    match command:
        case Command.HAS.value:
            assert file is not None, "Вы не указали атрибут --file"

            db = get_db()
            has_file: bool = False
            
            if file in db:
                has_file = True

            print(f"Файл {file} присутствует" if has_file else f"Файл {file} отсутствует")
        case Command.READ.value:
            assert file is not None, "Вы не указали атрибут --file"
            
            db = get_db()
            db_file = db.get(file) # type: ignore
            
            if db_file is None:
                print(f"Файл {file} отсутствует")
                return
            
            db_host_list = db_file.keys()
            result: dict[str,bytes] = {}
            db_file_block_count: None | int = None
            for db_host in db_host_list:
                host, port = db_host.split(":")
                db_block_id_list = db_file[db_host]

                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

                try:
                    s.connect((host, int(port)))
                except BlockingIOError as e:
                    print("BlockingIOError")

                for db_block_id in db_block_id_list:
                    if db_file_block_count is None:
                        db_file_block_count = int(db_block_id.split(":")[0])
                    request_data = f"{Command.READ.value}:{file}:{db_block_id}"

                    s.send(bytes(request_data, 'UTF-8'))

                    response_data = s.recv(2048).decode("UTF-8")
                    response_data_items = response_data.split(":")
                    result[db_block_id] = bytes(response_data_items.pop().encode("utf-8")) # type: ignore
                s.close()

            block_items = list(result.values())
            if len(block_items) != db_file_block_count:
                return

            data = reduce(concatenate, block_items)
            print(f"Файл {file} {data}" )
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


if __name__ == "__main__":
    main()
