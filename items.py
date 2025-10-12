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
            "intel": "0 Cost, 100 Item health, 0.5 second repair time, 5 to 10 damage, 50% critical, 115% critical damage",
            "cost": 0,
            "max_health": 100,
            "repair_time": 0.5,
            "attack_range": (5, 10),
            "critical_chance": 0.5,
            "critical_damage": 1.15
        })
    
    def generate_attack(self) -> str:
        return random.choice((
            "Let the sword swosh through the air!",
            "Try to pierce him straight in the heart!"
        ))

class SteelSword(ItemProtocol):
    def __init__(self):
        super().__init__(ItemType.ATTACK, {
            "name": "Steel Sword",
            "desc": "A strong and solid steel sword",
            "intel": "10 Cost, 120 Item health, 0.4 second repair time, 7 to 13 damage, 30% critical, 125% critical damage",
            "cost": 10,
            "max_health": 120,
            "repair_time": 0.4,
            "attack_range": (7, 13),
            "critical_chance": 0.3,
            "critical_damage": 1.25
        })
    
    def generate_attack(self) -> str:
        return random.choice((
            "Let the sword swosh into the leg!",
            "Drag him into the sword!"
        ))

# ---- Armor ----

class WoodenArmor(ItemProtocol):
    def __init__(self):
        super().__init__(ItemType.SHIELD, {
            "name": "Wooden Armor",
            "desc": "Wooden armor is a simple way to protect your body",
            "intel": "0 Cost, 100 Item health (shielding), 1.5 second repair time",
            "cost": 0,
            "health": 100,
            "repair_time": 1.5,
            "attack_range": (0, 0),
            "critical_chance": 0.0,
            "critical_damage": 0
        })

class SteelArmor(ItemProtocol):
    def __init__(self):
        super().__init__(ItemType.SHIELD, {
            "name": "Steel Armor",
            "desc": "Steel armor is stronger than wooden",
            "intel": "10 Cost, 150 Item health (shielding), 2.0 second repair time",
            "cost": 10,
            "health": 150,
            "repair_time": 2.0,
            "attack_range": (0, 0),
            "critical_chance": 0.0,
            "critical_damage": 0
        })

# ---- Library ----

class ItemLibrary:
    items: List[ItemProtocol] = [
        WoodenSword(),
        WoodenArmor(),
        SteelSword(),
        SteelArmor()
    ]
    weapons: Dict[str, ItemProtocol] = {i.name: i for i in items if i.itype == ItemType.ATTACK}
    armor: Dict[str, ItemProtocol] = {i.name: i for i in items if i.itype == ItemType.SHIELD}

    all_by_name: Dict[str, ItemProtocol] = {
        i.name: i.__class__ for i in items
    }
    inventory_by_name: Dict[str, ItemProtocol] = {
        i.name: i for i in items
    }

    @classmethod
    def generate_weapon(cls) -> ItemProtocol:
        return random.choice((
            WoodenSword(),
        ))
    
    @classmethod
    def generate_armor(cls) -> ItemProtocol:
        return random.choice((
            WoodenArmor(),
        ))