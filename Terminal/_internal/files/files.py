from typing import Iterable, Tuple, List, Optional, TypeVar
from pathlib import Path
from ..builder import Builder
from ..core import Terminal
from .enums import ItemType

__all__ = (
    "Item",
    "File",
    "Directory"
)

T = TypeVar("T", bound="Item")

class Item:
    itype: ItemType

    def __init__(self, path: Path, parent: Optional["Item"] = None):
        self.path = path
        self.parent = parent

    @classmethod
    def load(cls: type[T], path: Path, parent: Optional[T] = None) -> Optional[T]:
        if not cls.check_validity(path):
            return None
        return cls(path, parent)

    @staticmethod
    def check_validity(path: Path) -> bool:
        raise NotImplementedError

    @property
    def exists(self) -> bool:
        raise NotImplementedError

    @property
    def name(self) -> str:
        return self.path.name

    @property
    def anchor(self) -> str:
        return self.path.anchor

    def load_parent(self) -> Optional["Directory"]:
        return Directory.load(self.path.parent)

    def absolute(self) -> str:
        return str(self.path.absolute())

    def update(self) -> None:
        raise NotImplementedError

class File(Item):
    itype = ItemType.FILE

    def __init__(self, path: Path, parent: Optional["Directory"] = None):
        super().__init__(path, parent)
        self.content: str = ""
        self.update()

    @staticmethod
    def check_validity(path: Path) -> bool:
        return path.is_file()

    @property
    def exists(self) -> bool:
        return self.path.is_file()

    def update(self) -> None:
        self.content = self.path.read_text()

    def write(self, content: str) -> None:
        self.path.write_text(content)
        self.content = content

class Directory(Item):
    itype = ItemType.DIRECTORY

    def __init__(self, path: Path, parent: Optional["Directory"] = None):
        super().__init__(path, parent)
        self.directories: List["Directory"] = []
        self.files: List[File] = []
        self.update()

    @staticmethod
    def check_validity(path: Path) -> bool:
        return path.is_dir()

    @property
    def exists(self) -> bool:
        return self.path.is_dir()

    def update(self) -> None:
        self.load_directories()
        self.load_files()

    def walk(self) -> Iterable[Tuple[Path, List[str], List[str]]]:
        dirs, files = [], []
        for entry in self.path.iterdir():
            if entry.is_dir():
                dirs.append(entry.name)
            elif entry.is_file():
                files.append(entry.name)
        yield self.path, dirs, files

        for entry in self.path.iterdir():
            if entry.is_dir():
                subdir = Directory.load(entry, self)
                if subdir:
                    yield from subdir.walk()

    def load_directories(self) -> None:
        self.directories.clear()
        for entry in self.path.iterdir():
            if entry.is_dir():
                directory = Directory.load(entry, self)
                if directory:
                    self.directories.append(directory)

    def load_files(self) -> None:
        self.files.clear()
        for entry in self.path.iterdir():
            if entry.is_file():
                file = File.load(entry, self)
                if file:
                    self.files.append(file)


class FileManager:
    def __init__(self, top: Directory):
        self.page = Builder()
        self.top = top
        self.current: Item = top
        self.input_field = Terminal.IOString()

    def _render_directory(self) -> None:
        self.current.update()
        for directory in getattr(self.current, "directories", []):
            self.page.print(directory.absolute())
        for file in getattr(self.current, "files", []):
            self.page.print(file.absolute())

    def _render_file(self) -> None:
        self.current.update()
        self.page.print(getattr(self.current, "content", ""))

    def print(self) -> None:
        self.page.clear()
        if self.current.itype == ItemType.DIRECTORY:
            self._render_directory()
        elif self.current.itype == ItemType.FILE:
            self._render_file()
        self.page.render(end="")

    def input(self) -> Optional[str]:
        Terminal.space()
        self.input_field.clear()
        self.input_field.input(f"{self.current.absolute()}>")
        command = self.input_field.value.strip()

        # Navigate to parent
        if command == "..":
            self.current = self.current.parent or self.current.load_parent() or self.top
            return None

        # Navigate inside directory
        if self.current.itype == ItemType.DIRECTORY:
            for directory in self.current.directories:
                if command in (directory.absolute(), directory.name):
                    self.current = directory
                    return None
            for file in self.current.files:
                if command in (file.absolute(), file.name):
                    self.current = file
                    return None

        return command