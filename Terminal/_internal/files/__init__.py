from .files import File, Directory, FileManager
from .enums import ItemType

__all__ = ("FileSystem",)

class FileSystem:
    File = File
    Directory = Directory
    FileManager = FileManager
    ItemType = ItemType