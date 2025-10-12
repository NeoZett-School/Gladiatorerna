# What we can't see on screen

from typing import Tuple, List, Dict, Optional, Any, Type, Self, TypedDict
from enum import Enum, auto
from names import generate_name
from story import generate_story
from items import ItemLibrary
from Saves import SaveHandler
import System
import random

class DifficultyData(TypedDict):
    desc: str
    enemy_max_health_factor: float
    enemy_base_attack: int
    enemy_critical_factor: float
    enemy_encounters: Dict[int, Tuple[int, int]] 
    # enemy encounters: What level for what levels of the enemy to occur
    rewards: Dict[int, Dict[str, Any]] 
    # rewards: first of, the level to reach, second, dict with string identifiers 
    # for item to be increased by it's value.
    # These are also the loses (25% of these) if you lose.

class CONFIG: # We can configure this game here
    difficulty_data: Dict[str, DifficultyData] = { 
        # These are the real effects of the difficulty,
        # except for the other implementations that are 
        # dependent on what difficulty it is. 
        # (Then we use the enum directly)
        "Easy": {
            "desc": "The easiest. If you just want to try the experience.",
            "enemy_max_health_factor": 0.75,
            "enemy_healing": 1.25,
            "enemy_base_attack": 8,
            "enemy_critical_factor": 0.75,
            "enemy_encounters": {
                1: (1, 1),
                2: (1, 3),
                3: (1, 4),
                4: (1, 5),
                5: (1, 5)
            },
            "rewards": {
                2: {
                    "points": 50,
                    "exp": 0.5
                },
                3: {
                    "points": 100,
                    "exp": 0.5
                }
            }
        },
        "Normal": {
            "desc": "Normal. Use this to get some action!",
            "enemy_max_health_factor": 1.0,
            "enemy_healing": 1.0,
            "enemy_base_attack": 10,
            "enemy_critical_factor": 1.0,
            "enemy_encounters": {
                1: (1, 1),
                2: (1, 3),
                3: (1, 4),
                4: (1, 5),
                5: (1, 5)
            },
            "rewards": {
                2: {
                    "points": 10,
                    "exp": 0.25
                },
                3: {
                    "points": 30,
                    "exp": 0.25
                }
            }
        },
        "Hard": {
            "desc": "The challenge is to beat this!",
            "enemy_max_health_factor": 1.25,
            "enemy_healing": 0.75,
            "enemy_base_attack": 15,
            "enemy_critical_factor": 1.15,
            "enemy_encounters": {
                1: (1, 1),
                2: (1, 4),
                3: (1, 6),
                4: (1, 7),
                5: (1, 7)
            },
            "rewards": {
                2: {
                    "points": 5,
                    "exp": 0.15
                },
                3: {
                    "points": 15,
                    "exp": 0.15
                }
            }
        }
    }
    characters: Dict[str, System.PlayerData] = {
        "Jim": { # The casual baddie
            "name": "Jim",
            "desc": "The default male protagonist.",
            "max_health": 100,
            "healing": 1.0,
            "base_attack": 10,
            "critical_chance": 0.5,
            "critical_factor": 1.0,
        },
        "Tessa": {
            "name": "Trickedy Tessa", # This is only the displayed name
            "desc": "The female protagonist.",
            "max_health": 150, # We're tough!
            "healing": 0.75,
            "base_attack": 5,
            "critical_chance": 0.65,
            "critical_factor": 0.95,
        }
    }
    enemy_attack_text = {
        "Alex": ["He slashes the sword at you.", "He uses the power of minecraft!"],
        "default": ["They punsh you like a punshing bag!", "They hit you right in the stomach."]
    }

class Difficulty(Enum): # enums allow setting a state
    Easy = auto()
    Normal = auto()
    Hard = auto()

    @property
    def data(self) -> DifficultyData: # We can get the corresponding data
        return CONFIG.difficulty_data.get(self.name, {})
    
    @classmethod
    def get(cls, name: str) -> Optional["Difficulty"]:
        if not isinstance(name, str):
            return None
        name = name.capitalize()  # normalize input like "easy" -> "Easy"
        return cls.__members__.get(name)

class Player(System.Handler): # We inherit the handler to create a player
    def __init__(self, name: str) -> Self:
        super().__init__()
        self.sys: System.Player = System.Player(CONFIG.characters[name.capitalize()])
    
    def on_update(self) -> None:
        self.sys.update()

class Enemy(System.Handler): # The full enemy implementation.
    def __init__(self, name: str, level: int, difficulty: Difficulty) -> Self:
        super().__init__()
        self.sys: System.Enemy = System.Enemy({
            "name": name,
            "level": level,
            "max_health": 100 * difficulty.data.get("enemy_max_health_factor" ,1.0),
            "healing": difficulty.data.get("enemy_healing", 1.0),
            "base_attack": difficulty.data.get("enemy_base_attack", 10) + level,
            "critical_chance": 0.5,
            "critical_factor": difficulty.data.get("enemy_critical_factor", 1.0)
        })
    
    def on_update(self) -> None:
        self.sys.update()
    
    def generate_attack(self) -> str:
        return random.choice(CONFIG.enemy_attack_text.get(self.sys.name, CONFIG.enemy_attack_text["default"]))

    @classmethod
    def generate_enemy(cls, player: Player, difficulty: Difficulty) -> Self:
        min_level, max_level = difficulty.data.get("enemy_encounters", {}).get(player.sys.level, (1, 1))
        enemy = cls(generate_name(), random.randint(min_level, max_level), difficulty)
        player_weapons = list(i for i in player.sys.items if i.equipped and i.itype == System.ItemType.ATTACK)
        player_armor = list(i for i in player.sys.items if i.equipped and i.itype == System.ItemType.SHIELD)
        weapon_grades = list(i.upgrades for i in player_weapons)
        armor_grades = list(i.upgrades for i in player_armor)
        max_weapon_grade = max(weapon_grades)
        max_armor_grade = max(armor_grades)
        weapon_count = random.randint(1, len(player_weapons))
        armor_count = random.randint(1, len(player_armor))
        def add_item(i: System.ItemProtocol) -> None:
            nonlocal enemy
            enemy.sys.items.append(i)
            i.owner = enemy.sys
            i.equipped = True
        for _ in range(weapon_count):
            item = ItemLibrary.generate_weapon(enemy.sys.level)
            item._data["upgrades"] = random.randint(1, max_weapon_grade)
            add_item(item)
        for _ in range(armor_count):
            item = ItemLibrary.generate_armor(enemy.sys.level)
            item._data["upgrades"] = random.randint(1, max_armor_grade)
            add_item(item)
        return enemy

class Environment:
    # Here, we define the environment.
    # f.e backstory, enemy, rewards. 
    # Anything in a fight.
    def __init__(self, player: Player, enemy: Enemy, difficulty: Difficulty) -> Self:
        self.player: Player = player
        self.enemy: Enemy = enemy
        self.story: List[str] = generate_story()
        self.rewards: Dict[str, Any] = difficulty.data.get("rewards", {}).get(player.sys.level + 1, {})
        self._story_index: int = 0
    
    @property
    def next(self) -> str:
        text = self.story[self._story_index]
        return text
    
    def move_on(self) -> None:
        self._story_index += 1
        if self._story_index > len(self.story) - 1:
            self._story_index = 0

class Section(System.Handler):
    handlers: List[System.Handler]
    def __init__(self) -> Self:
        self.handlers = []
    def init(self) -> None: # Replicate the actual system
        for handler in self.handlers:
            handler._system = self.system
            handler.init()
    @property
    def system(self) -> "Game": # We want the correct typing
        return super().system
    def on_update(self) -> None:
        for handler in self.handlers:
            handler.on_update()
    def on_render(self) -> None:
        for handler in self.handlers:
            handler.on_render()
    def tick(self) -> None:
        ...

class SectionManager: 
    # This will load and handle initialization of different sections.
    # The difference is that this class dynamically handles sections, 
    # whilst the library only statically stores them.

    sections: Dict[str, Section] = {}

    @classmethod
    def load_section(cls, name: str, section: Section) -> None: 
        # Load the section into the manager
        cls.sections[name] = section
    
    @classmethod
    def init_section(cls, game: "Game", name: str) -> None:
        # Initialize the section into the game system
        game.handlers = [cls.sections[name]]
        game.init()

class Game(System.System):
    # We'll build the actual game mechanics here
    def __init__(self) -> Self:
        super().__init__()

        self.save_handler: SaveHandler = SaveHandler()
        self.difficulty: Difficulty = Difficulty.Normal
        self.char_name: str = "Jim" 
        self.save_file: str = ""
        self.player: Optional[Player] = None # Initalized later.
        self.environment: Optional[Environment] = None
    
    def update(self) -> None:
        super().update()
    
    def render(self) -> None:
        super().render()