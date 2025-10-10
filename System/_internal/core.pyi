# .pyi is the equivelent of a C interface.
# It contains types and other code without runtime.
# This follows pep-561, with type defintions in a 
# .pyi file with everything the real runtime file 
# has. This improves runtime, structure and 
# readability.

from typing import Tuple, List, Optional, Protocol, runtime_checkable
from .data import PlayerData, ItemData

def clear_screen() -> None:
    """Clear the screen"""
    ...

class Player:
    items: List[ItemProtocol]

    """A player will play the game."""
    def __init__(self, _data: Optional[PlayerData] = None) -> None:
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
    def protec(self) -> int:
        """The protection the player wears."""
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
    def damage(self) -> int:
        """The total attack of the player."""
        ...
    def attack(self, damage: int) -> bool:
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

    equipped: bool

    # This will contain whatever structure any item will have.
    # It will also provide default values, easing the item making...
    def __init__(self, _data: Optional[ItemData] = None):
        ...
    @property
    def name(self) -> str:
        ...
    @property
    def desc(self) -> str:
        ...
    @property
    def cost(self) -> int:
        ...
    @property
    def health(self) -> int:
        ...
    @property
    def protec(self) -> int:
        ...
    @property
    def repair_time(self) -> float:
        ...
    @property
    def attack_range(self) -> Tuple[int, int]:
        ...
    @property
    def critical_chance(self) -> float:
        ...
    @property
    def critical_damage(self) -> int:
        ...
    def attack(self, damage: int) -> bool:
        ...
    def update(self) -> None:
        ...

class Handler(Protocol):
    """A handler will handle any update or rendering."""
    def __init__(self):
        ...
    @property
    def system(self) -> None:
        ...
    def on_update(self) -> None:
        ...
    def on_render(self) -> None:
        ...

class System:
    """The Gladiator game system."""
    active: bool
    handlers: List[Handler]
    def __init__(self):
        """Create a new system"""
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