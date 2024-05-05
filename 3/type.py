import typing

DataBaseHost = typing.NewType('DataBaseHost', str)
DataBaseBlockId = typing.NewType('DataBaseBlockId', str)
DataBaseFilePathName = typing.NewType('DataBaseFilePathName', str)
DataBaseFile = typing.NewType('DataBaseFile', dict[DataBaseHost,list[DataBaseBlockId]])
DataBase = typing.NewType('DataBase', dict[DataBaseFilePathName,DataBaseFile])

FileSystemFilePathName = typing.NewType('FileSystemFilePathName', str)
FileSystemBlockId = typing.NewType('FileSystemBlockId', str)
FileSystem = typing.NewType('FileSystem', dict[FileSystemFilePathName, dict[FileSystemBlockId, bytes]])
