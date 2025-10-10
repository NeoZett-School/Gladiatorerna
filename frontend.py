# What we can see on screen

from typing import Dict
import colorama
import backend

colorama.init()

class MenuSection(backend.Section):
    def on_render(self) -> None:
        super().on_render()
        print(f"Welcome to {colorama.Fore.CYAN}Gladiatorerna{colorama.Fore.RESET}!")
        print("")
        print("Where would you like to go?")
        options = {
            # id, title, section
            "1": (f"{colorama.Fore.GREEN}Start{colorama.Fore.RESET}", "Game"),
            "2": (f"{colorama.Fore.CYAN}Settings{colorama.Fore.RESET}", "Settings"),
            "3": (f"{colorama.Fore.RED}Exit{colorama.Fore.RESET}", "Exit")
        }
        for k, v in options.items():
            print(f"{k}: {v[0]}")
        solution = options.get(input("Select one option: ").lower().strip())
        if not solution: return

        if solution[1] == "Exit":
            self.system.quit()
            return
        
        backend.SectionManager.init_section(self.system, solution[1])

class SettingsSection(backend.Section):
    def on_render(self) -> None:
        super().on_render()
        print("Options:")
        options = {
            # id, title, current value
            "1": ("Difficulty", self.system.difficulty.name)
        }
        for k, v in options.items():
            print(f"{k}: {v[0]} [{v[1]}]")
        print("")
        # We are continuing here later

class GameSection(backend.Section):
    def on_render(self) -> None:
        ...

class SectionLibrary: 
    # We create all sections and load them one by one.
    sections: Dict[str, backend.Section] = {
        "Menu": MenuSection(),
        "Settings": SettingsSection(),
        "Game": GameSection()
    }

    @classmethod
    def load(cls) -> None:
        """Load all sections into the manager."""
        for name, section in cls.sections.items():
            backend.SectionManager.load_section(name, section)

SectionLibrary.load()

game = backend.Game()
backend.SectionManager.init_section(game, "Menu")
game.run()