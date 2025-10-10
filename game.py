from typing import List, Dict, Any
from enum import Enum, auto
import System
import random

class CONFIG: # We can configure this game here
    difficulty_data: Dict[str, Dict[str, Any]] = { 
        # These are the real effects of the difficulty,
        # except for the other implementations that are 
        # dependent on what difficulty it is. 
        # (Then we use the enum directly)
        "Easy": {},
        "Normal": {},
        "Hard": {}
    }

class Difficulty(Enum): # enums allow setting a state
    Easy = auto()
    Normal = auto()
    Hard = auto()

    @property
    def data(self) -> Dict[str, Any]: # We can get the corresponding data
        return CONFIG.difficulty_data.get(self.name, {})

class Player(System.Handler): # We inherit the handler to create a player
    def __init__(self, name: str):
        super().__init__()
        self.player: System.Player = System.Player({
            "name": name,
            "exp": 0.0,
            "level": 1,
            "health": 100,
            "base_attack": 10,
            "critical_chance": 0.5,
            "critical_factor": 1.0
        })

class Enemy(System.Handler): # The full enemy implementation.
    def __init__(self, name: str, level: int):
        super().__init__()
        self.enemy: System.Enemy = System.Enemy({
            "name": name,
            "health": random.randint(100 * level * 2, 100 * level * 2.15 + 50),
            "level": level,
            "attack_range": (
                random.randint(10 * level, 20 * level)
            )
        })

class Section(System.Handler):
    handlers: List[System.Handler]
    def __init__(self):
        self.handlers = []
    def init(self) -> None: # Replicate the actual system
        for handler in self.handlers:
            handler._system = self.system
            handler.init()
    def on_update(self) -> None:
        for handler in self.handlers:
            handler.on_update()
    def on_render(self) -> None:
        for handler in self.handlers:
            handler.on_render()
    def tick(self) -> None:
        ...

class MenuSection(Section):
    def tick(self):
        ...

class Game(System.System):
    # We'll build the actual game mechanics here
    def __init__(self):
        super().__init__()
        self.section: Section
    
    def update(self) -> None:
        super().update()
        ... # We'll expand here
    
    def render(self) -> None:
        super().render()