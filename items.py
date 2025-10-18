# Here, we create all items (Weapons and armour) that you can buy or use in the game.

from typing import List, Dict, Optional
from System import ItemProtocol, ItemType
import random

# ---- Weapons ----

class WoodenSword(ItemProtocol):
    itype = ItemType.ATTACK
    def __init__(self):
        super().__init__({
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
    itype = ItemType.ATTACK
    def __init__(self):
        super().__init__({
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

class FireBow(ItemProtocol):
    itype = ItemType.ATTACK
    def __init__(self):
        super().__init__({
            "name": "Fire Bow",
            "desc": "A strong, dangerous bow. This bow does not only deal, damage. But also -- procedually -- fire damage!",
            "intel": "15 Cost, 5 Item health, 2.5 second repair time, 5 to 10 damage, 40% critical, 115% critical damage, 20 fire damage, 3 minimal level",
            "cost": 15,
            "max_health": 5,
            "repair_time": 2.5,
            "attack_range": (5, 10),
            "critical_chance": 0.4,
            "critical_damage": 1.15,
            "fire_damage": 5,
            "minimal_level": 3
        })
    
    def generate_attack(self) -> str:
        return random.choice((
            "Let the arrow swosh into his arm!",
            "Shoot the arrow, his head is the goal."
        ))

# ---- Armor ----

class WoodenArmor(ItemProtocol):
    itype = ItemType.SHIELD
    def __init__(self):
        super().__init__({
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
    itype = ItemType.SHIELD
    def __init__(self):
        super().__init__({
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
        WoodenSword,
        WoodenArmor,
        SteelSword,
        SteelArmor,
        FireBow
    ]

    weapons: List[ItemProtocol] = list(i for i in items if i.itype == ItemType.ATTACK)
    armor: List[ItemProtocol] = list(i for i in items if i.itype == ItemType.SHIELD)

    class Inventory:
        # Weapons and armor will make up the player inventory completely.
        items: List[ItemProtocol]
        weapons: Dict[str, ItemProtocol]
        armor: Dict[str, ItemProtocol]

        def __init__(self) -> None:
            self.items = list(i() for i in ItemLibrary.items) # Build inventory
            self.weapons = {i.name: i for i in self.items if i.itype == ItemType.ATTACK}
            self.armor = {i.name: i for i in self.items if i.itype == ItemType.SHIELD}
        
        def get_by_name(self, name: str) -> Optional[ItemProtocol]:
            if name in self.weapons: return self.weapons[name]
            if name in self.armor: return self.armor[name]
            return

    @classmethod
    def generate_weapon(cls, level: int) -> ItemProtocol:
        return random.choice(cls.weapons[:min(level + 1, len(cls.weapons))])()
    
    @classmethod
    def generate_armor(cls, level: int) -> ItemProtocol:
        return random.choice(cls.armor[:min(level + 1, len(cls.armor))])()