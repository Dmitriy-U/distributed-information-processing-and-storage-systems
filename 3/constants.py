FILE_SYSTEM: dict[str, dict[str, bytes]] = {
    "/test.txt": {
        "2:1": b"0xff",
        "2:2": b"0x00"
    }
}

HOST = "127.0.0.255"

PORT = 9999

BYTE_BLOCK_LENGTH = 1024

EXTERNAL_NODE_COUNT = 1
