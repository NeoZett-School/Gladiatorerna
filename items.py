# Here, we create all items (Weapons and armour) that you can buy or use in the game.

from typing import List, Dict
from System import ItemProtocol, ItemType
import random

# ---- Weapons ----

class WoodenSword(ItemProtocol):
    def __init__(self):
        super().__init__(ItemType.ATTACK, {
            "name": "Wooden Sword",
            "desc": "A basic wooden sword",
            "intel": "0 Cost, 100 Item health, 1 second repair time, 5 to 10 damage, 50% critical, 115% critical damage",
            "cost": 0,
            "max_health": 100,
            "repair_time": 1,
            "attack_range": (5, 10),
            "critical_chance": 0.5,
            "critical_damage": 1.15
        })
    
    def generate_attack(self) -> str:
        return random.choice((
            "Let the sword swosh through the air!",
            "Try to pierce him straight in the heart!"
        ))

# ---- Armor ----

class WoodenArmor(ItemProtocol):
    def __init__(self):
        super().__init__(ItemType.SHIELD, {
            "name": "Wooden Armor",
            "desc": "Wooden armor is a simple way to protect your body",
            "intel": "0 Cost, 100 Item health (shielding), 1 second repair time",
            "cost": 0,
            "health": 100,
            "repair_time": 1,
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