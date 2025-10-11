from typing import List
import random

stories: List[List[str]] = [
    [
        "The enemy stands in front of you, the sun in his face. This was the perfect opportunity.",
    ],
]

def generate_story() -> List[str]:
    return random.choice(stories)