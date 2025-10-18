# Checkout the .pyi

from typing import Tuple, List, Optional, Self, Protocol, runtime_checkable
from .data import PlayerData, ItemData
from .itemtypes import ItemType
from .terminal import Terminal
import random
import time

__all__ = (
    "Player",
    "Enemy",
    "ItemProtocol",
    "Handler",
    "System"
)

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
        return int(self._data.get("health", self.max_health))
    
    @property
    def max_health(self) -> int:
        return int(self._data.get("max_health", 100) * (1 + self.level * 0.25)) + sum(i.max_health for i in self.items if i.equipped and i.itype == ItemType.SHIELD)
    
    @property
    def healing(self) -> float:
        return self._data.get("healing", 1) * max(1 - self.level * 0.25, 0.25)
    
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
    def fire_damage(self) -> float:
        return self._data.get("fire_damage", 0.0)
    
    @property
    def attack(self) -> int:
        critical_factor = self.critical_factor if self.critical_chance < random.uniform(0, 1) else 1.0
        level_factor = (1 + self.level * 0.25)
        return int(self.base_attack * critical_factor * level_factor)
    
    @property
    def is_dead(self) -> bool:
        return self.health <= 0
    
    @property
    def equipped_weapons(self) -> List["ItemProtocol"]:
        return list(i for i in self.items if i.equipped and i.itype == ItemType.ATTACK)
    
    def damage(self, damage: int) -> int:
        for shield in self.items:
            if shield.itype == ItemType.SHIELD and shield.equipped:
                absorbed = max(shield.health, 0)
                shield.damage(damage)
                damage -= absorbed
        if damage <= 0:
            return
        self._data["health"] -= damage
        return damage
    
    def update(self) -> None:
        for item in self.items:
            item.update()
        current_time = time.monotonic()
        if current_time >= self._next_heal:
            times = max(1, int((current_time - self._next_heal) // self.healing))
            self._data["health"] = min(self.health + times * (1 - self.fire_damage * 0.75), self.max_health)
            self._next_heal = current_time + self.healing
            self._data["fire_damage"] = (self.fire_damage - (0.15 * times)) if self.fire_damage > 0 else 0

class Enemy(Player):
    ...

@runtime_checkable
class ItemProtocol(Protocol): 
    itype: ItemType
    def __init__(self, _data: Optional[ItemData] = None) -> Self:
        self._data: ItemData = _data or {}
        self._next_repair: float = time.monotonic()
        self.owner: Optional[Player] = None
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
        return int(self._data.get("max_health", 100) * (1 + self.upgrades * 0.25))
    
    @property
    def repair_time(self) -> float:
        return max(self._data.get("repair_time", 0.0) - (self.upgrades * 0.05), 0.25)
    
    @property
    def attack_range(self) -> Tuple[int, int]:
        return self._data.get("attack_range", (0, 1))
    
    @property
    def critical_chance(self) -> float:
        return self._data.get("critical_chance", 0.0)
    
    @property
    def critical_damage(self) -> float:
        return self._data.get("critical_damage", 0.0)
    
    @property
    def fire_damage(self) -> float:
        return self._data.get("fire_damage", 0.0) * (1 + (self.upgrades - 1) * 0.25)
    
    @property
    def upgrades(self) -> int:
        return int(self._data.get("upgrades", 0))
    
    @property
    def upgrade_cost(self) -> int:
        return int((self.cost if self.cost > 0 else 9) * (1 + self.upgrades) * 1.5)
    
    @property
    def minimal_level(self) -> int:
        return int(self._data.get("minimal_level", 0))
    
    @property
    def owned(self) -> bool:
        return bool(self.owner) and self in self.owner.items
    
    def damage(self, damage: int) -> None:
        new_health = self.health - damage
        self._data["health"] = int(new_health)
    
    def update(self) -> None:
        current_time = time.monotonic()
        if current_time >= self._next_repair:
            times = max(1, int((current_time - self._next_repair) // self.repair_time))
            self._data["health"] = min(self.health + times, self.max_health)
            self._next_repair = current_time + self.repair_time
    
    def use(self, other: Player) -> Tuple[bool, int]:
        if not self.itype == ItemType.ATTACK: return False, 0
        if self.health > 0:
            effective_health_ratio = max(0, self.health - 10) / self.max_health
            this_attack = int(random.randint(*self.attack_range) * (1 + min(effective_health_ratio, 1.0)))
            is_ctitical = self.critical_chance < random.randint(0, 1)
            critical = self.critical_damage if is_ctitical else 1.0
            total_damage = int((self.owner.attack + this_attack) * (1 + self.upgrades * 0.25) * critical)
            other._data["fire_damage"] = other.fire_damage + self.fire_damage
            other.damage(total_damage)
            self.damage(total_damage)
            return is_ctitical, total_damage
        return False, 0

    def buy(self, player: Player) -> bool:
        if player.points < self.cost:
            return False
        player._data["points"] = player.points - self.cost
        player.items.append(self)
        self.owner = player
        self.equipped = True
        return True
    
    def upgrade(self) -> bool:
        if self.owner.points < self.upgrade_cost:
            return False
        self.owner._data["points"] = self.owner.points - self.upgrade_cost
        self._data["upgrades"] = self.upgrades + 1
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
        Terminal.clear()
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