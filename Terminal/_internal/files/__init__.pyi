from typing import Type
from .files import File, Directory, FileManager
from .enums import ItemType

class FileSystem:
    """
    Built as a simple file traversal program.
    You can utilize this to build complex file systems.
    """
    File: Type[File]
    Directory: Type[Directory]
    FileManager: Type[FileManager]
    ItemType: Type[ItemType]