# Checkout the .pyi

from typing import Tuple, List, Optional, Protocol, runtime_checkable
from .data import PlayerData, EnemyData, ItemData
import random
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
        self.items: List[ItemProtocol] = []

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
        return int(self._data.get("health", 100)) + sum(i.health for i in self.items if i.equipped)
    
    @property
    def protec(self) -> int:
        return sum(i.protec for i in self.items)
    
    @property
    def base_attack(self) -> int:
        return int(self._data.get("base_attack", 0))
    
    @property
    def critical_chance(self) -> float:
        return self._data.get("critical_chance", 0.0)
    
    @property
    def critical_factor(self) -> float:
        return self._data.get("critical_factor", 0.0)
    
    @property
    def damage(self) -> int:
        return int(
            self.base_attack + 
            sum(random.randint(i.attack_range[0], i.attack_range[1]) for i in self.items if i.equipped) * 
            (
                sum(i.critical_damage for i in self.items if random.uniform(0, 1) < i.critical_chance and i.equipped) * self.critical_factor 
                if random.uniform(0, 1) < self.critical_chance else 1
            )
        )
    
    def attack(self, damage: int) -> bool:
        for item in self.items:
            if item.attack(damage):
                self._data["health"] = self.health - damage
        if self.health < 0:
            return True
        return False
    
    def update(self) -> None:
        ...

class Enemy(Player):
    ...

@runtime_checkable
class ItemProtocol(Protocol): 
    def __init__(self, _data: Optional[ItemData] = None):
        self._data: ItemData = _data or {}
        self._next_repair: float = time.monotonic()
        self.equipped: bool = False

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
    def protec(self) -> int:
        return int(self._data.get("protec", 0))
    
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
    
    def attack(self, damage: int) -> bool:
        self._data["health"] = self.health - damage
        if self.health < 0:
            return True
        return False
    
    def update(self) -> None:
        ...

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