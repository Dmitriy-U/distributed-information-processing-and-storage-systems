from type import FileSystem


FILE_SYSTEM: FileSystem = {
    "test.txt": {
        "2:1": b"0xff",
        "2:2": b"0x00"
    }
} # type: ignore

HOST = "127.0.01"

PORT_FROM_MAIN = 9000

PORT_FROM_STORAGE = 9100

BYTE_BLOCK_LENGTH = 8

EXTERNAL_NODE_COUNT = 1

DB_PATH_NAME = 'hosts-data.json'
