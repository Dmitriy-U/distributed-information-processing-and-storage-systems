from app.models import Base
from app.crud import db_delete_file, db_get_file_blocks, db_get_file_storages
from app.constants import BYTE_BLOCK_LENGTH
from app.database import SessionLocal, engine
from app.helpers import Command, get_config, get_file_data, parse_args_main, storage_delete_file


Base.metadata.create_all(bind=engine)


def main():
    (command, file, file_source, block, block_data) = parse_args_main()

    match command:
        case Command.READ.value:
            assert file is not None, "Вы не указали атрибут --file"
            
            with SessionLocal() as session:
                db_file_blocks = db_get_file_blocks(session, file)
            
            assert len(db_file_blocks) > 0, f"Файл {file} отсутствует"

            file_data = get_file_data(db_file_blocks)
            
            print(f"Файл {file} {file_data}")
        case Command.WRITE.value:
            assert file is not None, "Вы не указали атрибут --file"
            assert file_source is not None, "Вы не указали атрибут --file-source"
            
            config = get_config()
            host_list: list[str] = config.get('hostList', None)
            
            assert host_list is not None, "Вы не указали атрибут --host-list"

            # db_file = write_file(file, file_source, host_list)
            # if db_file is None:
            #     print(f"Файл {file} не был записан")
            #     return
            
            # db = get_db()
            # db[file] = db_file
            # set_db(db)
            
            print(f"Файл {file} был записан")
        case Command.DELETE.value:
            assert file is not None, "Вы не указали атрибут --file"

            with SessionLocal() as session:
                db_file_blocks = db_get_file_storages(session, file)
                
                storage_addresses: set[str] = set()
                for block in db_file_blocks:
                    storage_addresses.add(block[0])
                    
                is_deleted = storage_delete_file(file, storage_addresses)
                
                if is_deleted:
                    db_delete_file(session, file)
            
            print(f"Файл {file} удалён" if is_deleted else f"Файл {file} не был удалён")
        case Command.CHANGE_BLOCK.value:
            assert file is not None, "Вы не указали атрибут --file"
            assert block is not None, "Вы не указали атрибут --block"
            assert block_data is not None, "Вы не указали атрибут --block-data"
            assert len(block_data) == BYTE_BLOCK_LENGTH, f"Длина блока длжна составлять {BYTE_BLOCK_LENGTH}"

            # db = get_db()
            # db_file = db.get(file, None)
            
            # assert db_file is not None, f"Файл {file} отсутствует"
            
            # block_changed = change_block_file(db_file, file, block, block_data)

            # if block_changed:
            #     print(f"Блок {block} файла {file} изменён")
            # else:
            #     print(f"Блок {block} файла {file} не изменён")
        case _:
            print("Команда отсутствует")
            exit(0)


if __name__ == "__main__":
    main()
