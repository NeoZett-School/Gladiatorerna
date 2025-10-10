# .pyi is the equivelent of a C interface.
# It contains types and other code without runtime.
# This follows pep-561, with type defintions in a 
# .pyi file with everything the real runtime file 
# has. This improves runtime, structure and 
# readability.

from typing import Tuple, List, Optional, Self, Protocol, runtime_checkable
from .data import PlayerData, ItemData
from .itemtypes import ItemType

def clear_screen() -> None:
    """Clear the screen"""
    ...

class Player:
    items: List[ItemProtocol]

    """A player will play the game."""
    def __init__(self, _data: Optional[PlayerData] = None) -> Self:
        ...
    @property 
    def name(self) -> str:
        """The name of the player."""
        # The property will work as a unchangeable variable. You can only get the value, unless if you have a "name.setter"
        # decorating another function in the same environment.
        ...
    @property
    def points(self) -> float:
        """How much points the player has."""
        ...
    @property
    def exp(self) -> float:
        """The player experience."""
        ...
    @property
    def level(self) -> int:
        """The player level."""
        ...
    @property
    def health(self) -> int:
        """The player health."""
        ...
    @property
    def max_health(self) -> int:
        """The max health of this player."""
        ...
    @property
    def healing(self) -> float:
        """How fast this player heals."""
        ...
    @property
    def base_attack(self) -> int:
        """The base attack of this player."""
        ...
    @property
    def critical_chance(self) -> float:
        """The base critical chance of this player."""
        ...
    @property
    def critical_factor(self) -> float:
        """The critical damage factor."""
        ...
    @property
    def attack(self) -> int:
        """The total attack of the player."""
        ...
    def damage(self, damage: int) -> bool:
        """Attack the player."""
        ...
    
    def update(self) -> None:
        """Update the player and all its items."""
        ...

class Enemy(Player):
    """The enemy."""
    ...

@runtime_checkable # Runtime checkable ensures "isinstance(var, ItemProtocol)"
class ItemProtocol(Protocol): 
    """Any item."""

    owner: Optional[Player]
    itype: ItemType
    equipped: bool

    # This will contain whatever structure any item will have.
    # It will also provide default values, easing the item making...
    def __init__(self, itype: ItemType, _data: Optional[ItemData] = None) -> Self:
        """Initialize this item."""
        ...
    @property
    def name(self) -> str:
        """The name of this item."""
        ...
    @property
    def desc(self) -> str:
        """The description of this item."""
        ...
    @property
    def cost(self) -> int:
        """The cost of this item."""
        ...
    @property
    def health(self) -> int:
        """The health of this item"""
        ...
    @property
    def max_health(self) -> int:
        """The max health of this item."""
        ...
    @property
    def repair_time(self) -> float:
        """The time in seconds for it to repair."""
        ...
    @property
    def attack_range(self) -> Tuple[int, int]:
        """The low and high damage of the item."""
        ...
    @property
    def critical_chance(self) -> float:
        """The critical chance of this item."""
        ...
    @property
    def critical_damage(self) -> int:
        """The critical damage of this item."""
        ...
    def damage(self, damage: int) -> bool:
        """Damage this item."""
        ...
    def update(self) -> None:
        """Update this item."""
        ...
    def use(self, other: Player) -> None:
        """Use this item against another player."""
        ...
    def buy(self, player: Player) -> bool:
        """Buy this item as the given player."""
        ...

class Handler(Protocol):
    """A handler will handle any update or rendering."""
    @property
    def system(self) -> "System":
        ...
    def init(self) -> None:
        ...
    def on_update(self) -> None:
        ...
    def on_render(self) -> None:
        ...
    def tick(self) -> None:
        ...

class System:
    """The Gladiator game system."""
    active: bool
    handlers: List[Handler]
    def __init__(self) -> Self:
        """Create a new system"""
        ...
    def init(self) -> None: 
        """Initialize all handlers."""
        ...
    def update(self) -> None:
        """Update the system."""
        ...
    def render(self) -> None:
        """Render the game."""
        ...
    def tick(self) -> None:
        """Simulate a new game tick."""
        ...
    def run(self) -> None:
        """Run the game."""
        ...
    def quit(self) -> None:
        """Quit the game."""
        ...