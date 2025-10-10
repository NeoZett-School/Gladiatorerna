# What we can't see on screen

from typing import List, Dict, Optional, Any, Self
from enum import Enum, auto
from names import generate_name
from story import generate_story
import System
import items
import random

class CONFIG: # We can configure this game here
    difficulty_data: Dict[str, Dict[str, Any]] = { 
        # These are the real effects of the difficulty,
        # except for the other implementations that are 
        # dependent on what difficulty it is. 
        # (Then we use the enum directly)
        "Easy": {
            "desc": "The easiest. If you just want to try the experience.",
            "enemy_max_health_factor": 0.5
        },
        "Normal": {
            "desc": "Normal. Use this to get some action!",
            "enemy_max_health_factor": 1.0
        },
        "Hard": {
            "desc": "The challenge is to beat this!",
            "enemy_max_health_factor": 1.5
        }
    }
    characters: Dict[str, System.PlayerData] = {
        "Jim": { # The casual baddie
            "name": "Jim",
            "desc": "The default male protagonist.",
            "exp": 0.0,
            "level": 1,
            "max_health": 100,
            "healing": 1.0,
            "base_attack": 10,
            "critical_chance": 0.5,
            "critical_factor": 1.0
        }
    }

class Difficulty(Enum): # enums allow setting a state
    Easy = auto()
    Normal = auto()
    Hard = auto()

    @property
    def data(self) -> Dict[str, Any]: # We can get the corresponding data
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
        self.player: System.Player = System.Player(CONFIG.characters[name.capitalize()])

class Enemy(System.Handler): # The full enemy implementation.
    def __init__(self, name: str, level: int, difficulty: Difficulty) -> Self:
        super().__init__()
        self.enemy: System.Enemy = System.Enemy({
            "name": name,
            "level": level,
            "max_health": 100 * (1 + level * 0.25) * difficulty.data.get("enemy_max_health_factor" ,1.0)
        })

    @classmethod
    def generate_enemy(cls, min_level: int, max_level: int, difficulty: Difficulty) -> Self:
        return cls(generate_name(), random.randint(min_level, max_level), difficulty)

class Environment:
    # Here, we define the environment.
    # f.e backstory, enemy, shop. 
    # Anything, really.
    def __init__(self, enemy: Enemy) -> Self:
        self.enemy: Enemy = enemy
        self.story: str = generate_story()

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

        self.difficulty: Difficulty = Difficulty.Normal
        self.char_name: str = "Jim" 
        # We'll initialize the player when we start the game.
        # We cannot go back to menu when the game is started.
    
    def update(self) -> None:
        super().update()
    
    def render(self) -> None:
        super().render()