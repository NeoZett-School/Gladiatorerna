# Checkout the .pyi

from typing import Tuple, List, Optional, Self, Protocol, runtime_checkable
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
    def __init__(self, _data: Optional[PlayerData] = None) -> Self:
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
        return int(self._data.get("level", 1))
    
    @property
    def health(self) -> int:
        return int(self._data.get("health", self.max_health) + sum(i.health for i in self.items if i.equipped and i.itype == ItemType.SHIELD))
    
    @property
    def max_health(self) -> int:
        return int(self._data.get("max_health", 100) + sum(i.max_health for i in self.items if i.equipped and i.itype == ItemType.SHIELD) * (1 + self.level * 0.25))
    
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
        critical_factor = self.critical_factor if self.critical_chance < random.uniform(0, 1) else 1.0
        level_factor = (1 + self.level * 0.25)
        return int(self.base_attack * critical_factor * level_factor)
    
    @property
    def equipped_weapons(self) -> List["ItemProtocol"]:
        return list(i for i in self.items if i.equipped and i.itype == ItemType.ATTACK)
    
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
            max_health = self._data.get("max_health", 100) * (1 + self.level * 0.25)
            self._data["health"] = min(self._data.get("health", max_health) + 1, max_health)
            self._next_heal = current_time + self.healing

class Enemy(Player):
    ...

@runtime_checkable
class ItemProtocol(Protocol): 
    def __init__(self, itype: ItemType, _data: Optional[ItemData] = None) -> Self:
        self._data: ItemData = _data or {}
        self._next_repair: float = time.monotonic()
        self.owner: Optional[Player] = None
        self.itype: ItemType = itype
        self.equipped: bool = False

    @property
    def name(self) -> str:
        return self._data.get("name", "Unknown")
    
    @property
    def desc(self) -> str:
        return self._data.get("desc", "<No description>")
    
    @property
    def intel(self) -> str:
        return self._data.get("intel", "<No intel>")
    
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
    def critical_damage(self) -> float:
        return self._data.get("critical_damage", 0.0)
    
    def damage(self, damage: int) -> int:
        result = min(self.health, 0)
        self._data["health"] = self.health - damage
        return damage - result
    
    def update(self) -> None:
        current_time = time.monotonic()
        if current_time >= self._next_repair:
            max_health = self._data.get("max_health", 100)
            self._data["health"] = min(self._data.get("health", max_health) + 1, max_health)
            self._next_repair = current_time + self.repair_time
    
    def use(self, other: Player) -> None:
        if not self.itype == ItemType.ATTACK: return
        if self.health <= 0:
            this_attack = random.randint(*self.attack_range)
            critical = self.critical_damage if self.critical_chance < random.randint(0, 1) else 1.0
            total_damage = int((self.owner.attack + this_attack) * critical)
            other.damage(total_damage)
            self.damage(total_damage)

    def buy(self, player: Player) -> bool:
        if player.points < self.cost:
            return False
        player._data["points"] = player.points - self.cost
        player.items.append(self)
        self.owner = player
        self.equipped = True
        return True

class Handler(Protocol):
    @property
    def system(self) -> "System":
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
    def __init__(self) -> Self:
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