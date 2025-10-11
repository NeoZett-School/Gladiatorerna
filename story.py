from typing import List
import random

stories: List[List[str]] = [
    [
        "The enemy stands in front of you, the sun in his face. This was the perfect opportunity.",
        "You throw dirt in his face. He must be blind. Take your chance!",
        "He fights back, and you stand face to face, again."
    ],
    [
        "He launches at you, giving you an almost nerve-shattering look. Oh, he must have so dangerous thoughts for what he'll do with you.",
        "Oh... He got a hit...",
        "He runs away, only to run back, straight into you!"
    ]
]

def generate_story() -> List[str]:
    return random.choice(stories)