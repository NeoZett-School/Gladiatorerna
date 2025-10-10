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
            print(f"{colorama.Fore.BLUE}{k}{colorama.Fore.RESET}: {v[0]}")
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
            "1": ("Difficulty", self.system.difficulty.name),
            "2": ("Character", self.system.char_name)
        }
        print(f"{colorama.Fore.BLACK}0{colorama.Fore.RESET}: Go back")
        for k, v in options.items():
            print(f"{colorama.Fore.BLUE}{k}{colorama.Fore.RESET}: {colorama.Fore.YELLOW}{v[0]}{colorama.Fore.RESET} [{colorama.Fore.MAGENTA}{v[1]}{colorama.Fore.RESET}]")
        solution = input("Select one setting to change: ").lower().strip()
        if solution == "0": 
            backend.SectionManager.init_section(self.system, "Menu")
            return
        solution = options.get(solution)
        if not solution: return
        print("")
        match solution[0]:
            case "Difficulty":
                print("Difficulties:")
                for name, difficulty in backend.Difficulty.__members__.items():
                    print(f"{colorama.Fore.MAGENTA}{name}{colorama.Fore.RESET} - {colorama.Fore.BLUE}{difficulty.data.get("desc", "No description available.")}{colorama.Fore.RESET}")
                new_difficulty = None
                while not new_difficulty:
                    new_difficulty = backend.Difficulty.get(input("Select one difficulty: "))
                    if not new_difficulty: print(f"{colorama.Fore.RED}Invalid{colorama.Fore.RESET}. Try again.")
                self.system.difficulty = new_difficulty
            case "Character":
                print("Characters:")
                for name, data in backend.CONFIG.characters.items():
                    print(f"{colorama.Fore.MAGENTA}{name}{colorama.Fore.RESET} - {colorama.Fore.BLUE}{data.get("desc", "No description available.")}{colorama.Fore.RESET}")
                new_character = None
                while not new_character:
                    new_character = input("Select one character: ")
                    if not new_character in backend.CONFIG.characters: 
                        print(f"{colorama.Fore.RED}Invalid{colorama.Fore.RESET}. Try again.")
                        new_character = None
                self.system.char_name = new_character

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