from enum import Enum, auto

__all__ = ("ItemType",)

class ItemType(Enum):
    DIRECTORY = auto()
    FILE = auto()