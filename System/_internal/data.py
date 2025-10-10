from typing import Tuple, TypedDict

__all__ = ( # You can only import these from this file!
    "PlayerData",
    "ItemData"
)

class PlayerData(TypedDict):
    # PlayerData will be a type that will serve as a dict,
    # but with predefined keys and value types.
    name: str
    exp: float
    level: int
    health: int
    max_health: int
    base_attack: int
    critical_chance: float
    critical_factor: float

class ItemData(TypedDict):
    name: str
    desc: str
    health: int # Is either dependent on usage (f.e swords) or will extend the player health
    protec: int # The protection of the armour. Not the extra health of the armour,
    #             but rather how much health of the other item it takes.
    repair_time: float # The time it takes to repair the item (may have multiple)
    attack_range: Tuple[int, int]
    critical_chance: float
    critical_damage: int