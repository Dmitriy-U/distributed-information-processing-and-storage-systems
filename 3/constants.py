from type import FileSystem, FileSystemBlockId, FileSystemFilePathName


FILE_SYSTEM = FileSystem({
    FileSystemFilePathName("test.txt"): {
        FileSystemBlockId("2:1"): b'',
        FileSystemBlockId("2:2"): b''
    }
})

BYTE_BLOCK_LENGTH = 8

EXTERNAL_NODE_COUNT = 1

DB_PATH_NAME = 'hosts-data.json'
