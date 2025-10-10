import random

NAMES = [
    "Alex",
    "Jack",
    "Harry",
    "Link",
    "Taro",
    "Fin",
    "Spoke",
    "Chan",
    "Dam",
    "Liam",
    "Henry",
]

def generate_name() -> str:
    return random.choice(NAMES)