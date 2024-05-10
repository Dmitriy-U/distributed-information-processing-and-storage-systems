from constants import BYTE_BLOCK_LENGTH
from helpers import Command, change_block_file, delete_file, get_config, get_file_data, has_file_in_db, parse_args_main, get_db, set_db, write_file


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

            db_file = write_file(file, file_source, host_list)
            if db_file is None:
                print(f"Файл {file} не был записан")
                return
            
            db = get_db()
            db[file] = db_file
            set_db(db)
            
            print(f"Файл {file} был записан")
        case Command.DELETE.value:
            assert file is not None, "Вы не указали атрибут --file"

            db = get_db()
            db_file = db.get(file, None)
            
            assert db_file is not None, f"Файл {file} отсутствует"
            
            is_deleted = delete_file(file, db_file)
            
            del db[file]
            set_db(db)
            
            print(f"Файл удалён" if is_deleted else f"Файл не был удалён")
        case Command.CHANGE_BLOCK.value:
            assert file is not None, "Вы не указали атрибут --file"
            assert block is not None, "Вы не указали атрибут --block"
            assert block_data is not None, "Вы не указали атрибут --block-data"
            assert len(block_data) == BYTE_BLOCK_LENGTH, f"Длина блока длжна составлять {BYTE_BLOCK_LENGTH}"

            db = get_db()
            db_file = db.get(file, None)
            
            assert db_file is not None, f"Файл {file} отсутствует"
            
            block_changed = change_block_file(db_file, file, block, block_data)

            if block_changed:
                print(f"Блок {block} файла {file} изменён")
            else:
                print(f"Блок {block} файла {file} не изменён")
        case _:
            print("Команда отсутствует")
            exit(0)


if __name__ == "__main__":
    main()
