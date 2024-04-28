

def has_handler(fs: dict[str,dict[str,bytes]], file: None | str) -> tuple[bool, str]:
    assert file is not None, "Вы не указали аргумент --file"

    has_file = file in fs

    if has_file:
        message = f"Файл {file} есть"
    else:
        message = f"Файл {file} отстствует"

    return has_file, message


def read_handler(fs: dict[str,dict[str,bytes]], file: None | str) -> dict[str,bytes]:
    assert file is not None, "Вы не указали аргумент --file"
    assert file in fs, f"Файл {file} отсутствует"

    return fs[file]
