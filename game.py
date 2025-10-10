from typing import Dict, Any
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

class Player(System.Handler): # We inherit the player
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

class Enemy(System.Handler):
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

class Game(System.System):
    def __init__(self):
        super().__init__()
    
    def update(self) -> None:
        super().update()

        for handler in self.handlers:
            if isinstance(handler, Player):
                handler.player
    
    def render(self) -> None:
        super().render()