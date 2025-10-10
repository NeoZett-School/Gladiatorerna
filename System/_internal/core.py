# Checkout the .pyi

from typing import Tuple, List, Optional, Protocol, runtime_checkable
from .data import PlayerData, ItemData
from .itemtypes import ItemType
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
        self._next_heal: float = time.monotonic()
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
        return int(self._data.get("health", self.max_health)) + sum(i.health for i in self.items if i.equipped)
    
    @property
    def max_health(self) -> int:
        return int(self._data.get("max_health", 100)) + sum(i.max_health for i in self.items)
    
    @property
    def healing(self) -> float:
        return self._data.get("healing", 1)
    
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
    def attack(self) -> int:
        weapon_damage = sum(random.randint(i.attack_range[0], i.attack_range[1]) for i in self.items if i.equipped)
        critical_factor = (
            sum(i.critical_damage for i in self.items if random.uniform(0, 1) < i.critical_chance and i.equipped) * self.critical_factor 
            if random.uniform(0, 1) < self.critical_chance else 1
        )
        return int(self.base_attack + weapon_damage * critical_factor)
    
    def damage(self, damage: int) -> int:
        for item in self.items:
            if not item.itype == ItemType.SHIELD:
                continue
            damage = item.damage(damage)
        result = min(self.health, damage)
        self._data["health"] = self.health - damage
        return result
    
    def update(self) -> None:
        for item in self.items:
            item.update()
        current_time = time.monotonic()
        if current_time >= self._next_heal:
            self._data["health"] = min(self.health + 1, self.max_health)
            self._next_heal = current_time + self.healing

class Enemy(Player):
    ...

@runtime_checkable
class ItemProtocol(Protocol): 
    def __init__(self, itype: ItemType, _data: Optional[ItemData] = None):
        self._data: ItemData = _data or {}
        self._next_repair: float = time.monotonic()
        self.itype: ItemType = itype
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
        return int(self._data.get("health", self.max_health))
    
    @property
    def max_health(self) -> int:
        return int(self._data.get("max_health", 100))
    
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
    
    def damage(self, damage: int) -> int:
        result = min(self.health, 0)
        self._data["health"] = self.health - damage
        return damage - result
    
    def update(self) -> None:
        current_time = time.monotonic()
        if current_time >= self._next_repair:
            self._data["health"] = min(self.health + 1, self.max_health)
            self._next_repair = current_time + self.repair_time
    
    def use(self, other: Player) -> None:
        ...

class Handler(Protocol):
    @property
    def system(self) -> None:
        return self._system # If not defined, it will raise an error.
    
    def init(self) -> None: # When initializing this handler
        ...

    def on_update(self) -> None: # Second (Update logic)
        ...

    def on_render(self) -> None: # Last (Render the current state)
        ...
    
    def tick(self) -> None: # Runs first (Internal)
        ...

class System:
    active: bool
    handlers: List[Handler]
    def __init__(self):
        self.active = False
        self.handlers = []
    
    def init(self) -> None: 
        # Must be called or else the handlers will not work properly
        for handler in self.handlers:
            handler._system = self
            handler.init()

    def update(self) -> None:
        for handler in self.handlers:
            handler.on_update()

    def render(self) -> None:
        clear_screen()
        for handler in self.handlers:
            handler.on_render()

    def tick(self) -> None:
        for handler in self.handlers:
            handler.tick()
        self.update()
        self.render()

    def run(self) -> None:
        self.active = True
        while self.active:
            self.tick()
    
    def quit(self) -> None:
        self.active = False