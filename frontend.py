# What we can see on screen

from typing import Tuple, List, Dict, Self
import colorama
import backend
from items import ItemLibrary

colorama.init()

class MenuSection(backend.Section):
    def on_render(self) -> None:
        super().on_render()
        print(f"Welcome to {colorama.Fore.CYAN + colorama.Style.BRIGHT}Gladiatorerna{colorama.Fore.RESET + colorama.Style.RESET_ALL}!")
        print("")
        print("Where would you like to go?")
        options = {
            # id, title, section
            "1": (f"{colorama.Fore.GREEN}Start{colorama.Fore.RESET}", "Game"),
            "2": (f"{colorama.Fore.CYAN}Settings{colorama.Fore.RESET}", "Settings"),
        }
        exit_id = "3"
        if self.system.player: # If the game has initialized, we can safely reveal the shop!
            options["3"] = (f"{colorama.Fore.MAGENTA}Shop{colorama.Fore.RESET}", "Shop")
            exit_id = "4"
        options[exit_id] = (f"{colorama.Fore.RED}Exit{colorama.Fore.RESET}", "Exit")
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

class ShopSection(backend.Section):
    class Directory(backend.Section):
        items: List[Tuple[str, backend.System.ItemProtocol]]

        def init(self) -> None:
            super().init()
            self.shop: "ShopSection" = SectionLibrary.sections["Shop"]

        def on_render(self) -> None:
            super().on_render()
            self.shop.render_title()
            points = self.system.player.player.points
            print()
            self.shop.render_points(points)
            print()
            options = self.shop.render_items(points, self.items)
            solution = input("Select one item you want to buy: ").lower().strip()
            if solution == "0": 
                backend.SectionManager.init_section(self.system, "Shop")
                return
            solution = options.get(solution)
            if not solution: return
            if not solution.buy(self.system.player):
                print("You can't buy this item.")
                input("Press enter to continue...")
    
    class Weapons(Directory):
        items: List[Tuple[str, backend.System.ItemProtocol]] = [(n, i) for n, i in ItemLibrary.weapons.items()]

    class Armor(Directory): # Caching the items into a list that helps to unpack does also help with performance.
        items: List[Tuple[str, backend.System.ItemProtocol]] = [(n, i) for n, i in ItemLibrary.armor.items()]

    def on_render(self) -> None:
        super().on_render()

        if not self.system.player: # We are not initialized yet!
            backend.SectionManager.init_section(self.system, "Menu")
            return

        self.render_title()
        print("")
        options = {
            # id, title, section
            "1": (f"{colorama.Fore.RED}Weapons{colorama.Fore.RESET}", "Weapons"),
            "2": (f"{colorama.Fore.GREEN}Armor{colorama.Fore.RESET}", "Armor")
        }
        print(f"{colorama.Fore.BLACK}0{colorama.Fore.RESET}: Go back")
        for k, v in options.items():
            print(f"{colorama.Fore.BLUE}{k}{colorama.Fore.RESET}: {v[0]}")
        solution = input("Select one directory: ").lower().strip()
        if solution == "0": 
            backend.SectionManager.init_section(self.system, "Menu")
            return
        solution = options.get(solution)
        if not solution: return
        backend.SectionManager.init_section(self.system, solution[1])

    def render_title(self) -> None:
        print(f"---- {{{colorama.Fore.GREEN + colorama.Style.BRIGHT}SHOP{colorama.Fore.RESET + colorama.Style.RESET_ALL}}} ----")
    
    def render_points(self, points: int) -> None:
        print(f"Your points: {colorama.Fore.YELLOW + colorama.Style.BRIGHT}{points}p{colorama.Fore.RESET + colorama.Style.RESET_ALL}")
    
    def render_items(self, points: int, items: List[Tuple[str, backend.System.ItemProtocol]]) -> Dict[str, backend.System.ItemProtocol]:
        processed = {}
        print(f"{colorama.Fore.BLACK}0{colorama.Fore.RESET}: Go back")
        for i, (name, item) in enumerate(items):
            if item in self.system.player.player.items or item.owner == self.system.player.player: continue
            print(f"{colorama.Fore.BLUE}{i+1}{colorama.Fore.RESET}: {colorama.Fore.MAGENTA}{name}{colorama.Fore.RESET} [{(colorama.Fore.GREEN if points > item.cost else colorama.Fore.RED) + colorama.Style.BRIGHT}{item.cost}p{colorama.Fore.RESET + colorama.Style.RESET_ALL}] - {colorama.Fore.BLUE}{item.desc}{colorama.Fore.RESET}")
            processed[str(i+1)] = item
        return processed

class GameSection(backend.Section):
    def init(self) -> None:
        super().init()
        if not self.system.player: # Some options are unchangeable after starting the game, like the character
            self.system.player = backend.Player(self.system.char_name)

    def on_render(self) -> None:
        super().on_render()
        ...

class SectionLibrary: 
    # We create all sections and load them one by one.
    sections: Dict[str, backend.Section] = {
        "Menu": MenuSection(),
        "Settings": SettingsSection(),
        "Shop": ShopSection(),
        "Weapons": ShopSection.Weapons(),
        "Armor": ShopSection.Armor(),
        "Game": GameSection()
    }

    @classmethod
    def load(cls) -> None:
        """Load all sections into the manager."""
        for name, section in cls.sections.items():
            backend.SectionManager.load_section(name, section)

if __name__ == "__main__":
    SectionLibrary.load()

    game = backend.Game()
    backend.SectionManager.init_section(game, "Menu")
    game.run()