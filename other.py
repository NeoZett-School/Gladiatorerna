from typing import Dict
from enum import Enum, auto
import System

difficulty_data = {
    "Easy": {},
    "Normal": {},
    "Hard": {}
}

class Difficulty(Enum): # enums allow setting a state
    Easy = auto()
    Normal = auto()
    Hard = auto()

    @property
    def data(self):
        return difficulty_data.get(self.name, {})

class Player(System.Player): # We inherit the player
    def __init__(self, name: str):
        super().__init__({
            "name": name,
            "exp": 0.0,
            "level": 1,
            "health": 100,
            "base_attack": 10,
            "critical_chance": 0.5,
            "critical_factor": 1.0
        })