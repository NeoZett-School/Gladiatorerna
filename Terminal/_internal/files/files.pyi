from typing import Iterable, Tuple, List, Optional, Protocol, Self
from pathlib import Path
from ..builder import Builder
from ..core import Terminal
from .enums import ItemType

class Item(Protocol):
    itype: ItemType
    path: Path
    parent: Optional["Item"]

    def __init__(self, path: Path, parent: Optional["Item"] = None) -> Self:
        ...
    
    @classmethod
    def load(cls, path: Path, parent: Optional[Self] = None) -> Optional[Self]:
        ...
    
    @staticmethod
    def check_validity(path: Path) -> bool:
        ...
    
    @property
    def exists(self) -> bool:
        ...
    
    @property
    def name(self) -> str:
        ...
    
    @property
    def anchor(self) -> str:
        ...

    def load_parent(self) -> Optional["Directory"]:
        ...
    
    def absolute(self) -> str:
        ...
    
    def update(self) -> None:
        ...

class File(Item):
    content: str

    def __init__(self, path: Path, parent: Optional["Directory"] = None) -> Self:
        ...

    @staticmethod
    def check_validity(path: Path) -> bool:
        ...
    
    @property
    def exists(self) -> bool:
        ...
    
    def update(self) -> None:
        ...
    
    def write(self, content: str) -> None:
        ...

class Directory(Item):
    directories: List["Directory"]
    files: List[File]

    def __init__(self, path: Path, parent: Optional["Directory"] = None) -> Self:
        ...

    @staticmethod
    def check_validity(path: Path) -> bool:
        ...
    
    @property
    def exists(self) -> bool:
        ...
    
    def update(self) -> None:
        ...
    
    def walk(self) -> Iterable[Tuple[Path, List[str], List[str]]]:
        """Recursively yield (directory path, subdirectory names, file names)"""
        ...
    
    def load_directories(self) -> None:
        ...
    
    def load_files(self) -> None:
        ...

class FileManager:
    page: Builder
    current: Item
    top: Directory

    input_field: Terminal.IOString
    
    def __init__(self, top: Directory) -> Self:
        ...
    
    def print(self) -> None:
        """Print all directories and files onto the screen."""
        ...
    
    def input(self) -> Optional[str]:
        """Ask user for a input."""
        ...