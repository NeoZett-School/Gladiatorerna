# Checkout the .pyi

from typing import Tuple, List, Optional, Protocol, runtime_checkable
from .data import PlayerData, EnemyData, ItemData
import time
import os

__all__ = (
    "clear_screen",
    "Player",
    "Enemy",
    "ItemProtocol",
    "Handler",
    "System"
)

def clear_screen():
    os.system("cls")

class Player:
    def __init__(self, _data: Optional[PlayerData] = None) -> None:
        self._data: PlayerData = _data or {}

    @property 
    def name(self) -> str:
        return self._data.get("name", "Unknown")
    
    @property
    def points(self) -> float:
        return self._data.get("points", 0.0)
        
    @property
    def exp(self) -> float:
        return self._data.get("exp", 0.0)
    
    @property
    def level(self) -> int:
        return int(self._data.get("level", 0))
    
    @property
    def health(self) -> int:
        return int(self._data.get("health", 100))
    
    @property
    def base_attack(self) -> int:
        return int(self._data.get("base_attack", 0))
    
    @property
    def critical_chance(self) -> float:
        return self._data.get("critical_chance", 0.0)
    
    @property
    def critical_factor(self) -> float:
        return self._data.get("critical_factor", 0.0)

class Enemy:
    def __init__(self, _data: Optional[EnemyData] = None):
        self._data: EnemyData = _data or {}

    @property
    def name(self) -> str:
        return self._data.get("name", "Unknown")
    
    @property
    def health(self) -> int:
        return int(self._data.get("health", 0))
    
    @property
    def level(self) -> int:
        return int(self._data.get("level", 0))
    
    @property
    def attack_range(self) -> Tuple[int, int]:
        return self._data.get("attack_range", (0, 1))

@runtime_checkable
class ItemProtocol(Protocol): 
    def __init__(self, _data: Optional[ItemData] = None):
        self._data: ItemData = _data or {}
        self._next_repair: float = time.monotonic()

    @property
    def name(self) -> str:
        return self._data.get("name", "Unknown")
    
    @property
    def desc(self) -> str:
        return self._data.get("desc", "<No description>")
    
    @property
    def cost(self) -> int:
        return int(self._data.get("cost", 0))
    
    @property
    def health(self) -> int:
        return int(self._data.get("health", 0))
    
    @property
    def repair_time(self) -> float:
        return self._data.get("repair_time", 0.0)
    
    @property
    def attack_range(self) -> Tuple[int, int]:
        return self._data.get("attack_range", (0, 1))
    
    @property
    def critical_chance(self) -> float:
        return self._data.get("critical_chance", 0.0)
    
    @property
    def critical_damage(self) -> int:
        return int(self._data.get("critical_damage", 0))

class Handler(Protocol):
    @property
    def system(self) -> None:
        return self._system # If not defined, it will raise an error.

    def on_update(self) -> None:
        ...

    def on_render(self) -> None:
        ...

class System:
    active: bool
    handlers: List[Handler]
    def __init__(self):
        self.active = False
        self.handlers = []
    
    def init(self) -> None:
        for handler in self.handlers:
            handler._system = self

    def update(self) -> None:
        for handler in self.handlers:
            handler.on_update()

    def render(self) -> None:
        clear_screen()
        for handler in self.handlers:
            handler.on_render()

    def tick(self) -> None:
        self.update()
        self.render()

    def run(self) -> None:
        self.active = True
        while self.active:
            self.tick()
    
    def quit(self) -> None:
        self.active = False