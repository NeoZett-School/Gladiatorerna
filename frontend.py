# What we can see on screen

from typing import Dict
import backend

class MenuSection(backend.Section):
    def tick(self):
        ...

class SectionLibrary: 
    # We create all sections and load them one by one.
    sections: Dict[str, backend.Section] = {
        "Menu": MenuSection()
    }

    @classmethod
    def load(cls) -> None:
        """Load all sections into the manager."""
        for name, section in cls.sections.items():
            backend.SectionManager.load_section(name, section)

SectionLibrary.load()

game = backend.Game()
backend.SectionManager.init_section(game, "Menu")