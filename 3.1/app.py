import os

from app.models import Base
from app.crud import db_delete_file, db_get_file_block, db_get_file_blocks, db_get_file_storages
from app.constants import BYTE_BLOCK_LENGTH
from app.database import SessionLocal, engine
from app.helpers import Command, get_config, get_file_data, parse_args_main, storage_change_File_block, storage_delete_file, write_file


Base.metadata.create_all(bind=engine)


def main():
    (command, file_path, input, output, block_id, block_data) = parse_args_main()

    match command:
        case Command.READ.value:
            assert file_path is not None, "Вы не указали атрибут --file-path"
            
            with SessionLocal() as session:
                db_file_blocks = db_get_file_blocks(session, file_path)
            
            assert len(db_file_blocks) > 0, f"Файл {file_path} отсутствует"

            file_data = get_file_data(db_file_blocks)
            
            if output is None:
                print(file_data)
            else:
                with open(output, 'wb') as file:
                    file.write(file_data)

            exit(0)
        case Command.WRITE.value:
            assert file_path is not None, "Вы не указали атрибут --file-path"
            assert input is not None, "Вы не указали атрибут --input"
            
            config = get_config()
            host_list: list[str] = config.get('hostList', None)
            
            assert host_list is not None, "Вы не указали атрибут --host-list"

            with SessionLocal() as session:
                write_success = write_file(session, file_path, input, host_list)

            if not write_success:
                print(f"Файл {file_path} не был записан")
                exit(1)
                return
            
            print(f"Файл {file_path} был записан")
            exit(0)
        case Command.DELETE.value:
            assert file_path is not None, "Вы не указали атрибут --file-path"

            with SessionLocal() as session:
                db_file_blocks = db_get_file_storages(session, file_path)
                
                storage_addresses: set[str] = set()
                for block in db_file_blocks:
                    storage_addresses.add(block[0])
                    
                is_deleted = storage_delete_file(file_path, storage_addresses)
                
                if is_deleted:
                    db_delete_file(session, file_path)
            
            print(f"Файл {file_path} удалён" if is_deleted else f"Файл {file_path} не был удалён")
            exit(0)
        case Command.CHANGE_BLOCK.value:
            assert file_path is not None, "Вы не указали атрибут --file-path"
            assert block_id is not None, "Вы не указали атрибут --block-id"
            assert block_data is not None, "Вы не указали атрибут --block-data"
            assert len(block_data) == BYTE_BLOCK_LENGTH, f"Длина блока длжна составлять {BYTE_BLOCK_LENGTH} симвала"

            with SessionLocal() as session:
                db_file_block = db_get_file_block(session, file_path, block_id)

            assert db_file_block is not None, f"Файл {file_path} отсутствует"

            result = storage_change_File_block(db_file_block, block_data)
            # block_changed = change_block_file(db_file, file, block, block_data)

            # if block_changed:
            #     print(f"Блок {block} файла {file} изменён")
            # else:
            #     print(f"Блок {block} файла {file} не изменён")


if __name__ == "__main__":
    main()
