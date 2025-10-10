# Here, we create all items (Weapons and armour) that you can buy or use in the game.

from typing import List, Dict
from System import ItemProtocol, ItemType

class WoodenSword(ItemProtocol):
    def __init__(self):
        super().__init__(ItemType.ATTACK, {
            "name": "Wooden Sword",
            "desc": "A basic wooden sword.",
            "cost": 10,
            "health": 100,
            "protec": 0,
            "repair_time": 10,
            "attack_range": (5, 10),
            "critical_chance": 0.5,
            "critical_damage": 1
        })

class WoodenArmor(ItemProtocol):
    def __init__(self):
        super().__init__(ItemType.SHIELD, {
            "name": "Wooden Armor",
            "desc": "Wooden armor is a simple way to protect your body.",
            "cost": 10,
            "health": 100,
            "protec": 1,
            "repair_time": 10,
            "attack_range": (0, 0),
            "critical_chance": 0.0,
            "critical_damage": 0
        })

class ItemLibrary:
    items: List[ItemProtocol] = [
        WoodenSword(),
        WoodenArmor()
    ]
    weapons: Dict[str, ItemProtocol] = {i.name: i for i in items if i.itype == ItemType.ATTACK}
    armor: Dict[str, ItemProtocol] = {i.name: i for i in items if i.itype == ItemType.SHIELD}