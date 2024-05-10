from type import FileSystem, FileSystemBlockId, FileSystemFilePathName


FILE_SYSTEM = FileSystem({
    FileSystemFilePathName("test.txt"): {
        FileSystemBlockId("2:1"): b'12345678',
        FileSystemBlockId("2:2"): b'87654321'
    }
})

BYTE_BLOCK_LENGTH = 8

EXTERNAL_NODE_COUNT = 1

DB_PATH_NAME = 'hosts-data.json'
