from System import ItemProtocol

class WoodenSword(ItemProtocol):
    def __init__(self):
        super().__init__({
            "name": "Wooden Sword",
            "desc": "A basic wooden sword",
            "cost": 10,
            "health": 100,
            "protec": 0,
            "repair_time": 10,
            "attack_range": (5, 10),
            "critical_chance": 0.5,
            "critical_damage": 1
        })

class WoodenArmour(ItemProtocol):
    def __init__(self):
        super().__init__({
            "name": "Wooden Armour",
            "desc": "Wooden armour is a simple way to protect the body",
            "cost": 10,
            "health": 100,
            "protec": 1,
            "repair_time": 10,
            "attack_range": (0, 0),
            "critical_chance": 0.0,
            "critical_damage": 0
        })