# What we can see on screen
import colorama

print("Loading... (Bootup)", end="\r")

from typing import Tuple, List, Dict, Optional, Self, Any
from items import ItemLibrary # Import the item library
from System import print
import backend # Import the backend
import datetime
import random
import time
import sys
import os
import re

if not __name__ == "__main__":
    exit() # If this file was not run directly, we can simply exit like normal before anything get run.

colorama.init() # Initialize colorama

print("Loading... (Creating Objects)", end="\r")

class MenuSection(backend.Section): # We create a section for the menu
    def on_render(self) -> None: # On every render, we do...
        super().on_render() # Firstly, run the internal functionality from the parenting class
        print(f"Welcome to {colorama.Fore.CYAN + colorama.Style.BRIGHT}Gladiatorerna{colorama.Style.RESET_ALL}!")
        if not self.system.player:
            print("")
            print(f"{colorama.Style.BRIGHT}Before{colorama.Style.RESET_ALL} you {colorama.Fore.GREEN}Start{colorama.Style.RESET_ALL}, check that you have chosen"
                  f" your character in the {colorama.Fore.CYAN}Settings{colorama.Fore.RESET}.")
            print(f"The {colorama.Fore.MAGENTA}Shop{colorama.Fore.RESET} and {colorama.Fore.CYAN}Inventory{colorama.Fore.RESET}"
                  " will be unlocked once you've started the game and your character ")
            print("has been chosen. Once you have started, you can go back and buy new gear.")
            print("To do this, open the store. Then, you can go back into the battlefield, selecting"
                  f" {colorama.Fore.GREEN}Start{colorama.Fore.RESET}.")
        print("")
        print(f"Current time is: {colorama.Fore.YELLOW}{datetime.datetime.now().strftime("%H:%M")}{colorama.Fore.RESET}")
        print("")
        print("Where would you like to go?")
        options = {
            # id, title, section
            "1": (f"{colorama.Fore.GREEN}Start{colorama.Fore.RESET}", "Game"),
            "2": (f"{colorama.Fore.CYAN}Saves{colorama.Fore.RESET}", "Save"),
            "3": (f"{colorama.Fore.BLUE}About{colorama.Fore.RESET}", "About"),
            "4": (f"{colorama.Fore.YELLOW}Documentation{colorama.Fore.RESET}", "Documentation"),
            "5": (f"{colorama.Fore.CYAN}Settings{colorama.Fore.RESET}", "Settings"),
            "6": (f"{colorama.Fore.YELLOW}Intel{colorama.Fore.RESET}", "Intel")
        }
        exit_id = "7"
        if self.system.player: # If the game has initialized, we can safely reveal the shop!
            options["7"] = (f"{colorama.Fore.MAGENTA}Shop{colorama.Fore.RESET}", "Shop")
            options["8"] = (f"{colorama.Fore.LIGHTBLUE_EX}Blacksmith{colorama.Fore.RESET}", "Blacksmith")
            options["9"] = (f"{colorama.Fore.CYAN + colorama.Style.BRIGHT}Inventory{colorama.Style.RESET_ALL}", "Inventory")
            exit_id = "10"
        options[exit_id] = (f"{colorama.Fore.RED}Exit{colorama.Fore.RESET}", "Exit")
        for k, v in options.items():
            print(f"{colorama.Fore.BLUE}{k}{colorama.Fore.RESET}: {v[0]}")
        solution = options.get(input("Select one option: ").lower().strip())
        if not solution: return

        if solution[1] == "Exit": # Exit if we say so.
            self.system.quit()
            return
        
        if solution[1] == "Game" and not self.system.player:
            backend.SectionManager.init_section(self.system, "Loading")
            return
        
        backend.SectionManager.init_section(self.system, solution[1])

class SettingsSection(backend.Section): # Settings.
    def on_render(self) -> None:
        super().on_render()
        print("Options:")
        options = {
            # id, title, current value
            "1": ("Difficulty", self.system.difficulty.name),
        }
        if not self.system.player:
            options["2"] = ("Character", self.system.char_name)
        print(f"{colorama.Fore.RED}0{colorama.Fore.RESET}: Go back")
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
                if self.system.player:
                    print("[The new difficulty only apply once a new battle begins]")
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
    class Popup(backend.Section):
        def init(self) -> None:
            super().init()
            self.shop: "ShopSection" = SectionLibrary.sections["Shop"]
        
        def on_render(self) -> None:
            super().on_render()
            item = self.shop.to_buy
            options = {
                # id, title, code
                "1": (f"{colorama.Fore.GREEN + colorama.Style.BRIGHT}Yes{colorama.Style.RESET_ALL}", "Y"),
                "2": (f"{colorama.Fore.RED + colorama.Style.BRIGHT}No{colorama.Style.RESET_ALL}", "N")
            }
            print(f"Are you sure you want to buy {colorama.Fore.MAGENTA + colorama.Style.BRIGHT}{item.name}{colorama.Style.RESET_ALL}?")
            for k, v in options.items():
                print(f"{colorama.Fore.BLUE}{k}{colorama.Fore.RESET}: {v[0]}")
            solution = options.get(input("Select one option: ").lower().strip())
            if not solution: return
            if solution[1] == "Y":
                if not item.buy(self.system.player.sys):
                    print("You can't buy this item.")
                    input("Press enter to continue...")
            backend.SectionManager.init_section(self.system, "Shop")

    class Directory(backend.Section):
        items: List[Tuple[str, backend.System.ItemProtocol]]

        def init(self) -> None:
            super().init()
            self.shop: "ShopSection" = SectionLibrary.sections["Shop"]

        def on_render(self) -> None:
            super().on_render()
            self.shop.render_title()
            points = int(self.system.player.sys.points)
            print("")
            self.shop.render_points(points)
            self.shop.render_count(len(self.items))
            print("")
            print(f"{colorama.Fore.RED}0{colorama.Fore.RESET}: Go back")
            options = self.shop.render_items(points, self.items)
            solution = input("Select one item you want to buy: ").lower().strip()
            if solution == "0": 
                backend.SectionManager.init_section(self.system, "Shop")
                return
            solution = options.get(solution)
            if not solution: return
            self.shop.to_buy = solution
            backend.SectionManager.init_section(self.system, "Shop.Popup")
    
    class Weapons(Directory):
        def init(self) -> None:
            super().init()
            self.items = [i for i in self.system.player.inventory.weapons.values() if not i.owned and i.minimal_level <= self.system.player.sys.level]

    class Armor(Directory): # Caching the items into a list that helps to unpack does also help with performance.
        def init(self) -> None:
            super().init()
            self.items = [i for i in self.system.player.inventory.armor.values() if not i.owned and i.minimal_level <= self.system.player.sys.level]
    
    def init(self) -> None:
        super().init()
        self.to_buy: Optional[backend.System.ItemProtocol] = None
        self.items: int = list(i for i in self.system.player.inventory.items if not i.owned and i.minimal_level <= self.system.player.sys.level)

    def on_render(self) -> None:
        super().on_render()

        if not self.system.player: # We are not initialized yet!
            backend.SectionManager.init_section(self.system, "Menu")
            return

        self.render_title()
        print()
        self.render_points(int(self.system.player.sys.points))
        self.render_count(len(self.items))
        print()
        options = {
            # id, title, section
            "1": (f"{colorama.Fore.RED}Weapons{colorama.Fore.RESET}", "Shop.Weapons"),
            "2": (f"{colorama.Fore.GREEN}Armor{colorama.Fore.RESET}", "Shop.Armor")
        }
        print(f"{colorama.Fore.RED}0{colorama.Fore.RESET}: Go back")
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
        print(f"---- {{{colorama.Fore.GREEN + colorama.Style.BRIGHT}SHOP{colorama.Style.RESET_ALL}}} ----")
    
    def render_points(self, points: int) -> None:
        print(f"Your points: {colorama.Fore.YELLOW + colorama.Style.BRIGHT}{points}p{colorama.Style.RESET_ALL}")
    
    def render_count(self, count: int) -> None:
        print(f"Items for sale: {count}")
    
    def render_items(self, points: int, items: List[backend.System.ItemProtocol]) -> Dict[str, backend.System.ItemProtocol]:
        processed = {}
        for i, item in enumerate(items):
            if item.owned or not item.minimal_level <= self.system.player.sys.level: continue
            print(f"{colorama.Fore.BLUE}{i+1}{colorama.Fore.RESET}: {colorama.Fore.MAGENTA}{item.name}{colorama.Fore.RESET} [{(colorama.Fore.GREEN if points >= item.cost else colorama.Fore.RED) + colorama.Style.BRIGHT}{item.cost}p{colorama.Style.RESET_ALL}] - {colorama.Fore.BLUE}{item.desc}{colorama.Fore.RESET}")
            processed[str(i+1)] = item
        return processed

class InventorySection(backend.Section):
    class Directory(backend.Section):
        items: List[Tuple[str, backend.System.ItemProtocol]]

        def init(self) -> None:
            super().init()
            self.inv: "InventorySection" = SectionLibrary.sections["Inventory"]

        def on_render(self) -> None:
            super().on_render()
            self.inv.render_title()
            print()
            self.inv.render_count(len(self.items))
            print()
            print(f"{colorama.Fore.RED}0{colorama.Fore.RESET}: Go back")
            options = self.inv.render_items(self.items)
            solution = input("Select one item you want to change: ").lower().strip()
            if solution == "0": 
                backend.SectionManager.init_section(self.system, "Inventory")
                return
            solution = options.get(solution)
            if not solution: return
            solution.equipped = not solution.equipped
    
    class Weapons(Directory):
        def init(self) -> None:
            super().init()
            self.items = [(n, i) for n, i in self.system.player.inventory.weapons.items() if i.owned]

    class Armor(Directory): # Caching the items into a list that helps to unpack does also help with performance.
        def init(self) -> None:
            super().init()
            self.items = [(n, i) for n, i in self.system.player.inventory.armor.items() if i.owned]

    def on_render(self) -> None:
        super().on_render()

        if not self.system.player: # We are not initialized yet!
            backend.SectionManager.init_section(self.system, "Menu")
            return

        self.render_title()
        print()
        self.render_count(len(self.system.player.sys.items))
        print()
        options = {
            # id, title, section
            "1": (f"{colorama.Fore.RED}Weapons{colorama.Fore.RESET}", "Inventory.Weapons"),
            "2": (f"{colorama.Fore.GREEN}Armor{colorama.Fore.RESET}", "Inventory.Armor")
        }
        print(f"{colorama.Fore.RED}0{colorama.Fore.RESET}: Go back")
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
        print(f"---- {{{colorama.Fore.CYAN + colorama.Style.BRIGHT}Inventory{colorama.Style.RESET_ALL}}} ----")
    
    def render_count(self, count: int) -> None:
        print(f"Your items: {colorama.Fore.YELLOW + colorama.Style.BRIGHT}{count}{colorama.Style.RESET_ALL}")

    def render_items(self, items: List[Tuple[str, backend.System.ItemProtocol]]) -> Dict[str, backend.System.ItemProtocol]:
        processed = {}
        for i, (name, item) in enumerate(items):
            if not item.owned: continue
            print(f"{colorama.Fore.BLUE}{i+1}{colorama.Fore.RESET}: {colorama.Fore.MAGENTA}{name}{colorama.Fore.RESET} [{(colorama.Fore.GREEN if item.equipped else colorama.Fore.RED) + colorama.Style.BRIGHT}{"Equipped" if item.equipped else "Unequipped"}{colorama.Style.RESET_ALL}] - {colorama.Fore.BLUE}{item.desc}{colorama.Fore.RESET}")
            processed[str(i+1)] = item
        return processed

class IntelSection(backend.Section):
    def on_render(self) -> None:
        super().on_render()

        # Items
        print("Items:")
        def print_items(items: List[backend.System.ItemProtocol]) -> None:
            for item in items:
                if self.system.player:
                    owned = item in self.system.player.sys.items and item.owner == self.system.player.sys
                print(f"{colorama.Fore.MAGENTA}{item.name}{colorama.Fore.RESET}"
                    f"{f" ({colorama.Fore.YELLOW}{item.upgrades}{colorama.Fore.RESET})" \
                    f" [{(colorama.Fore.GREEN if item.equipped and owned else colorama.Fore.RED) + colorama.Style.BRIGHT}{"Equipped" if item.equipped else "Unequipped" if owned else "Not owned"}{colorama.Style.RESET_ALL}]" if self.system.player else ""}" 
                    f" - {colorama.Fore.BLUE}{item.desc}{colorama.Fore.RESET}")
                separator = f"\n{colorama.Fore.GREEN} - {colorama.Fore.YELLOW}"
                intel_raw = str(item.intel)  # Ensure it's a string

                # Function to color digits
                def color_numbers(text):
                    # Match integers or floats (e.g., 12, 0.45, 123.456)
                    pattern = r'\b\d+(?:\.\d+)?\b'
                    return re.sub(pattern, lambda m: f"{colorama.Fore.BLUE}{m.group(0)}{colorama.Fore.YELLOW}", text)

                # Build the formatted string
                intel_text = f"{colorama.Fore.YELLOW}Intel:{separator}{color_numbers(intel_raw)}{colorama.Fore.RESET}"

                # Apply the separator formatting
                formatted_output = separator.join(intel_text.split(", "))
                print(formatted_output)
        if self.system.player:
            print_items(self.system.player.inventory.items)
        else: print_items(list(i() for i in ItemLibrary.items))
        
        # Stats
        print("")
        print("Players:")
        if self.system.player:
            player = self.system.player.sys
            print(f"-- {colorama.Fore.YELLOW}{player.name}{colorama.Fore.RESET} --")
            print(f"{colorama.Fore.MAGENTA}[ YOU ]{colorama.Fore.RESET}")
            exp_have = max(int(player.exp*10), 0)
            exp_need = 10 - exp_have
            items = {
                # Title, value
                "Points": f"{int(player.points)}p",
                "Level": f"{player.level}",
                "Exp": f"{colorama.Fore.YELLOW}{"-"*exp_have}{colorama.Fore.BLUE}{"-"*exp_need}{colorama.Fore.RESET} ({int(player.exp*100)}%)",
                "Max Health": f"{player.max_health}",
                "Healing": f"{player.healing} seconds/hp",
                "Base Attack": f"{player.base_attack}",
                "Protection": f"{int(sum(i.max_health for i in player.items if i.equipped and i.itype == backend.System.ItemType.SHIELD))}",
                "Critical Chance": f"{player.critical_chance}",
                "Critical Factor": f"{player.critical_factor}"
            }
            for title, value in items.items():
                print(f"{colorama.Fore.YELLOW}{title}{colorama.Fore.RESET}: {colorama.Fore.BLUE}{value}{colorama.Fore.RESET}")
            print("")
        
        for name, data in backend.CONFIG.characters.items():
            if self.system.player and self.system.player.sys.name == name: continue
            print(f"-- {colorama.Fore.YELLOW}{name}{colorama.Fore.RESET} --")
            items = {
                # Title, value
                "Max Health": f"{data["max_health"]}",
                "Healing": f"{data["healing"]} seconds/hp",
                "Base Attack": f"{data["base_attack"]}",
                "Critical Chance": f"{data["critical_chance"]}",
                "Critical Factor": f"{data["critical_factor"]}"
            }
            for title, value in items.items():
                print(f"{colorama.Fore.YELLOW}{title}{colorama.Fore.RESET}: {colorama.Fore.BLUE}{value}{colorama.Fore.RESET}")
            print("")
                

        print("")
        print(f"{colorama.Fore.RED}0{colorama.Fore.RESET}: Go back")
        solution = input("Select one option: ").lower().strip()
        if solution == "0": 
            backend.SectionManager.init_section(self.system, "Menu")
            return

class BlacksmithSection(backend.Section):
    class Popup(backend.Section):
        def init(self) -> None:
            super().init()
            self.blacksmith: "BlacksmithSection" = SectionLibrary.sections["Blacksmith"]
        
        def on_render(self) -> None:
            super().on_render()
            item = self.blacksmith.to_upgrade
            options = {
                # id, title, code
                "1": (f"{colorama.Fore.GREEN + colorama.Style.BRIGHT}Yes{colorama.Style.RESET_ALL}", "Y"),
                "2": (f"{colorama.Fore.RED + colorama.Style.BRIGHT}No{colorama.Style.RESET_ALL}", "N")
            }
            print(f"Are you sure you want to upgrade {colorama.Fore.MAGENTA + colorama.Style.BRIGHT}{item.name}{colorama.Style.RESET_ALL}?")
            for k, v in options.items():
                print(f"{colorama.Fore.BLUE}{k}{colorama.Fore.RESET}: {v[0]}")
            solution = options.get(input("Select one option: ").lower().strip())
            if not solution: return
            if solution[1] == "Y":
                if not item.upgrade():
                    print("You can't upgrade this item.")
                    input("Press enter to continue...")
            backend.SectionManager.init_section(self.system, "Blacksmith")

    class Directory(backend.Section):
        items: List[Tuple[str, backend.System.ItemProtocol]]

        def init(self) -> None:
            super().init()
            self.blacksmith: "BlacksmithSection" = SectionLibrary.sections["Blacksmith"]

        def on_render(self) -> None:
            super().on_render()
            self.blacksmith.render_title()
            points = int(self.system.player.sys.points)
            print("")
            self.blacksmith.render_points(points)
            self.blacksmith.render_count(len(self.items))
            print("")
            print(f"{colorama.Fore.RED}0{colorama.Fore.RESET}: Go back")
            options = self.blacksmith.render_items(points, self.items)
            solution = input("Select one item you want to upgrade: ").lower().strip()
            if solution == "0": 
                backend.SectionManager.init_section(self.system, "Blacksmith")
                return
            solution = options.get(solution)
            if not solution: return
            self.blacksmith.to_upgrade = solution
            backend.SectionManager.init_section(self.system, "Blacksmith.Popup")
    
    class Weapons(Directory):
        def init(self) -> None:
            super().init()
            self.items = [(n, i) for n, i in self.system.player.inventory.weapons.items() if i.owned]

    class Armor(Directory): # Caching the items into a list that helps to unpack does also help with performance.
        def init(self) -> None:
            super().init()
            self.items = [(n, i) for n, i in self.system.player.inventory.armor.items() if i.owned]
    
    def init(self) -> None:
        super().init()
        self.to_upgrade: Optional[backend.System.ItemProtocol] = None
        self.items: int = list(i for i in self.system.player.inventory.items if i.owned)

    def on_render(self) -> None:
        super().on_render()

        if not self.system.player: # We are not initialized yet!
            backend.SectionManager.init_section(self.system, "Menu")
            return

        self.render_title()
        print("")
        self.render_points(int(self.system.player.sys.points))
        self.render_count(len(self.items))
        print("")
        options = {
            # id, title, section
            "1": (f"{colorama.Fore.RED}Weapons{colorama.Fore.RESET}", "Blacksmith.Weapons"),
            "2": (f"{colorama.Fore.GREEN}Armor{colorama.Fore.RESET}", "Blacksmith.Armor")
        }
        print(f"{colorama.Fore.RED}0{colorama.Fore.RESET}: Go back")
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
        print(f"---- {{{colorama.Fore.GREEN + colorama.Style.BRIGHT}BLACKSMITH{colorama.Style.RESET_ALL}}} ----")
    
    def render_points(self, points: int) -> None:
        print(f"Your points: {colorama.Fore.YELLOW + colorama.Style.BRIGHT}{points}p{colorama.Style.RESET_ALL}")
    
    def render_count(self, count: int) -> None:
        print(f"Items for upgrade: {count}")
    
    def render_items(self, points: int, items: List[Tuple[str, backend.System.ItemProtocol]]) -> Dict[str, backend.System.ItemProtocol]:
        processed = {}
        for i, (name, item) in enumerate(items):
            if not item.owned: continue
            print(f"{colorama.Fore.BLUE}{i+1}{colorama.Fore.RESET}: {colorama.Fore.MAGENTA}{name}{colorama.Fore.RESET} [{(colorama.Fore.GREEN if points >= item.upgrade_cost else colorama.Fore.RED) + colorama.Style.BRIGHT}{item.upgrade_cost}p{colorama.Style.RESET_ALL}] - {colorama.Fore.BLUE}{item.desc}{colorama.Fore.RESET}")
            processed[str(i+1)] = item
        return processed

class AboutSection(backend.Section):
    pages: List[List[str]] = [
        [
            "Gladiatorerna",
            "",
            "A game made in reality, in movies, in games.",
            "This game will let you take a trip into this",
            "very special place of ancient Rome."
        ],
        [
            "By Neo Zetterberg",
            "",
            "Link: https://github.com/neoostlundzetterberg-svg/Gladiatorerna"
        ]
    ]

    def init(self) -> None:
        super().init()
        self.index: int = 0

    @property
    def page(self) -> List[str]:
        if self.index <= len(self.pages) - 1:
            return self.pages[self.index]
        return f"{colorama.Fore.RED}Page {self.index} not found.{colorama.Fore.RESET}"
    
    def on_render(self) -> None:
        super().on_update()
        for text in self.page:
            print(text)
        print("")
        print(f"{colorama.Fore.RED}0{colorama.Fore.RESET}: Go back")
        print(f"{colorama.Fore.BLUE}1{colorama.Fore.RESET}: Next page")
        solution = input("Select one option: ").lower().strip()
        if solution == "0": 
            backend.SectionManager.init_section(self.system, "Menu")
            return
        elif solution == "1":
            self.index += 1
            if self.index > len(self.pages) - 1:
                self.index = 0
            return

class DocumentationSection(backend.Section):
    def __init__(self) -> Self:
        super().__init__()
        self.pages: List[List[str]] = []
        self.load_docs("docs.txt")
    
    def colorize_line(self, line: str, citation: bool) -> Tuple[str, bool]:
        """Apply color rules to a single line of documentation, including inline citations."""
        stripped = line.strip()

        # Handle full-line citations (lines starting with '>' or '"')
        if stripped.startswith(">") or stripped.startswith('"'):
            citation = True
            return f"{colorama.Fore.GREEN}{line}{colorama.Fore.RESET}", citation

        # Blank lines reset citation mode
        elif stripped == "":
            citation = False
            return line, citation

        # Headings (lines starting with '#')
        if line.startswith("#"):
            return f"{colorama.Fore.CYAN + colorama.Style.BRIGHT}{line}{colorama.Style.RESET_ALL}", citation

        # Bullet points
        if line.lstrip().startswith("- "):
            content = line.lstrip().removeprefix("- ").strip()
            return f"{colorama.Fore.YELLOW}- {colorama.Fore.RESET}{colorama.Fore.BLUE}{content}{colorama.Fore.RESET}", citation

        # Inline reset markers
        line = line.replace("$$", colorama.Fore.RESET)

        # --- Inline citations (segments between quotes) ---
        # Replace quoted segments with yellow color
        def colorize_quotes(match):
            inner = match.group(1)
            return f'{colorama.Fore.YELLOW}"{inner}"{colorama.Fore.RESET}{colorama.Fore.WHITE}'

        # Apply inline quote highlighting only if there are quote pairs
        if '"' in line:
            # Add base color first to ensure resets work cleanly
            line = f"{colorama.Fore.WHITE}" + re.sub(r'"(.*?)"', colorize_quotes, line) + colorama.Fore.RESET
        else:
            # If currently inside a multi-line citation, keep yellow
            if citation:
                line = f"{colorama.Fore.LIGHTBLUE_EX}{line}{colorama.Fore.RESET}"
            else:
                line = f"{colorama.Fore.WHITE}{line}{colorama.Fore.RESET}"

        return line, citation

    def load_docs(self, filename: str) -> None:
        """Load and parse the documentation file into colored pages."""
        with open(filename, "r", encoding="utf-8") as f:
            pages = f.read().split("\n---\n")

        for page in pages:
            total_page = []
            citation = False

            for line in page.splitlines():
                colored_line, citation = self.colorize_line(line, citation)
                total_page.append(colored_line)
            
            self.pages.append(total_page)

    def init(self) -> None:
        super().init()
        self.index: int = 0

    @property
    def page(self) -> List[str]:
        if self.index <= len(self.pages) - 1:
            return self.pages[self.index]
        return f"{colorama.Fore.RED}Page {self.index} not found.{colorama.Fore.RESET}"
    
    def on_render(self) -> None:
        super().on_update()
        for text in self.page:
            print(text)
        print("")
        print(f"{colorama.Fore.RED}0{colorama.Fore.RESET}: Go back")
        print(f"{colorama.Fore.BLUE}1{colorama.Fore.RESET}: Next page")
        solution = input("Select one option: ").lower().strip()
        if solution == "0": 
            backend.SectionManager.init_section(self.system, "Menu")
            return
        elif solution == "1":
            self.index += 1
            if self.index > len(self.pages) - 1:
                self.index = 0
            return

class SaveSection(backend.Section):
    class Save(backend.Section):
        def on_render(self) -> None:
            super().on_render()
            print(f"{colorama.Fore.CYAN + colorama.Style.BRIGHT}< NEW SAVE FILE >{colorama.Style.RESET_ALL}")
            file = input("Input a name for this file: ").strip()
            if not file.endswith(".json"): file = file+".json"
            data = self.system.player.sys._data

            items = self.system.player.sys.items
            data["items"] = { # Most compatible, could also do {dict_1} | {dict_2}
                i.name: {**{"equipped": i.equipped}, **i._data}
                for i in items
            }

            data["difficulty"] = self.system.difficulty.name

            self.system.save_handler.save(data, file)
            backend.SectionManager.init_section(self.system, "Save")

    def on_render(self) -> None:
        super().on_render()
        print(f"---- {{{colorama.Fore.CYAN}SAVE FILES{colorama.Fore.RESET}}} ----")
        print()
        if self.system.player: print(f"{colorama.Fore.BLUE}1{colorama.Fore.RESET}: Save")
        options = self.render_saves()
        for k, v in options.items():
            print(f"{colorama.Fore.BLUE}{k}{colorama.Fore.RESET}: {colorama.Fore.YELLOW}{v[0]}{colorama.Fore.RESET}")
        print(f"{colorama.Fore.RED}0{colorama.Fore.RESET}: Go back")
        solution = input("Select one option: ").lower().strip()
        if solution == "0":
            backend.SectionManager.init_section(self.system, "Menu")
            return
        elif solution == "1" and self.system.player:
            backend.SectionManager.init_section(self.system, "Save.Save")
            return
        solution = options.get(solution)
        if not solution: return
        player_data = self.system.save_handler.load(solution[1])

        self.system.difficulty = backend.Difficulty.get(player_data.pop("difficulty", "Normal"))

        player = backend.Player(player_data.get("name", "Unknown"))

        items = player_data.pop("items")
        for name, item_data in items.items():
            item = player.inventory.get_by_name(name)
            if not item: continue
            player.sys.items.append(item)
            item.owner = player.sys
            item.equipped = item_data.pop("equipped", True)
            item._data = item_data

        player.sys._data = player_data

        player.sys._data["health"] = player.sys.max_health
        for item in player.sys.items:
            item._data["health"] = item.max_health

        self.system.player = player
    
    def render_saves(self) -> Dict[str, Tuple[str, str]]:
        processed = {}
        for i, file in enumerate(self.system.save_handler.files):
            # id, title, path
            last_saved = self.system.save_handler.last_save.get(file, "Never")
            processed[str(i+2)] = (f"{os.path.splitext(os.path.basename(file))[0]} - last saved: {last_saved}", file)
        return processed

class LoadingSection(backend.Section):
    def init(self) -> None:
        super().init()
        self.frames: int = 0
        self.progression: int = 0
        self.interval: float = 0.05
        self.next_prog: float = time.monotonic() + self.interval
        self.symbol: int = 0

        self.loading_text: str = "-" * 10
    
    def on_update(self) -> None:
        self.frames += 1
        if self.frames % 5 == 0: # Performance!
            current_time = time.monotonic()
            if current_time >= self.next_prog:
                self.next_prog = current_time + self.interval
                self.progress()
            if self.progression % 4 == 0:
                self.increment_symbol()

    def on_render(self) -> None:
        super().on_render()
        print(
            f"\r{colorama.Fore.YELLOW}Bringing life to your gladiators... please wait. "
            f"{colorama.Fore.CYAN}Loading:{colorama.Fore.RESET} "
            f"{colorama.Fore.GREEN + colorama.Style.BRIGHT}{self.progression}% "
            f"{colorama.Fore.BLUE + colorama.Style.DIM}{self.from_symbol()}{colorama.Style.RESET_ALL} "
            f"[{self.loading_text}]"
        )
    
    def increment_symbol(self) -> None:
        self.symbol += 1
        if self.symbol > 3:
            self.symbol = 0
    
    def from_symbol(self) -> str:
        return ["-", "\\", "|", "/"][self.symbol]

    def progress(self) -> None:
        self.progression += 1
        if self.progression > 100:
            backend.SectionManager.init_section(self.system, "Game")
        else:
            factor = (self.progression / 100)
            count = int(10 * factor)
            self.loading_text = f"{colorama.Fore.GREEN + colorama.Style.BRIGHT}{"-" * count}{colorama.Fore.YELLOW + colorama.Style.DIM}{"-" * (10 - count)}{colorama.Style.RESET_ALL}"

class GameSection(backend.Section):
    class Directory(backend.Section):
        title: str
        rewards: Dict[str, Any]
        loss: bool = False
        def on_render(self) -> None:
            super().on_render()
            print(self.title)
            for reward, amount in self.rewards.items():
                player = self.system.player.sys
                amount = amount if not self.loss else -amount * 0.25
                match reward:
                    case "points":
                        player._data["points"] = player.points + amount
                    case "exp":
                        new_exp = player.exp + amount
                        while new_exp >= 1.0:
                            player._data["level"] = player.level + 1
                            new_exp -= 1.0
                        player._data["exp"] = new_exp
                    
                if not self.loss:
                    print(f"{colorama.Fore.YELLOW}{reward}{colorama.Fore.RESET} {colorama.Fore.GREEN + colorama.Style.BRIGHT}+{amount}{colorama.Style.RESET_ALL}")
                else:print(f"{colorama.Fore.YELLOW}{reward}{colorama.Fore.RESET} {colorama.Fore.RED + colorama.Style.BRIGHT}-{abs(amount)}{colorama.Style.RESET_ALL}")
            print("")
            options = {
                # id, title, code
                "1": (f"{colorama.Fore.GREEN + colorama.Style.BRIGHT}Yes{colorama.Style.RESET_ALL}", "Y"),
                "2": (f"{colorama.Fore.RED + colorama.Style.BRIGHT}No{colorama.Style.RESET_ALL}", "N")
            }
            print("Do you want to continue")
            for k, v in options.items():
                print(f"{colorama.Fore.BLUE}{k}{colorama.Fore.RESET}: {v[0]}")
            solution = options.get(input("Select one option: ").lower().strip())
            if not solution: return
            difficulty = self.system.difficulty
            self.system.environment = backend.Environment( # New environment time!
                self.system.player, 
                backend.Enemy.generate_enemy(
                    self.system.player,
                    difficulty
                ),
                difficulty
            )
            if solution[1] == "N":
                backend.SectionManager.init_section(self.system, "Menu")
                return
            backend.SectionManager.init_section(self.system, "Game")

    class Success(Directory):
        title = f"{colorama.Fore.GREEN}Success{colorama.Fore.RESET}! You won rewards: "
        def init(self) -> None:
            super().init()
            self.rewards = self.system.environment.rewards
    
    class Loss(Directory):
        title = f"Oh no! You {colorama.Fore.RED}lost{colorama.Fore.RESET} rewards: "
        def init(self) -> None:
            super().init()
            self.rewards = self.system.environment.rewards
            self.loss = True
    
    def __init__(self) -> Self:
        super().__init__()
        self.initialized: bool = False

    def init(self) -> None:
        super().init()

        if not self.initialized: 
            self.initialized = True
            # Some options are unchangeable after starting the game, like the character. 
            # Whilst some are only initialy created once.

            difficulty = self.system.difficulty

            # Setup the player
            if not self.system.player: # Only initialize the player if it isn't already there
                self.system.player = backend.Player(self.system.char_name)
                player = self.system.player
                player.inventory.weapons["Wooden Sword"].buy(player.sys)
                player.inventory.armor["Wooden Armor"].buy(player.sys)
                if difficulty == backend.Difficulty.Easy:
                    player.inventory.weapons["Steel Sword"].buy(player.sys)
                    player.inventory.armor["Steel Armor"].buy(player.sys)

            # Load the initial environment
            self.system.environment = backend.Environment(
                self.system.player, 
                backend.Enemy.generate_enemy(
                    self.system.player,
                    difficulty
                ),
                difficulty
            )

        self.log: Optional[List[str]] = None
        self.enemy_attack: str = self.system.environment.enemy.generate_attack()

    def on_render(self) -> None:
        super().on_render()
        print(f"---- {{{colorama.Fore.CYAN + colorama.Style.BRIGHT}GLADIATORERNA{colorama.Style.RESET_ALL}}} ----")
        print("")
        self.print_enemy()
        print(f"Round: {self.system.environment.round}")
        if self.log:
            print()
            self.print_log()
        print()
        self.print_stats()
        print("")
        print(f"{colorama.Fore.LIGHTYELLOW_EX}{self.system.environment.next}{colorama.Fore.RESET}")
        print("")
        print(self.enemy_attack)
        print("")
        print("What do you do?")
        options = self.render_items()
        print(f"{colorama.Fore.RED}0{colorama.Fore.RESET}: Go back")
        solution = input("Select one option: ").lower().strip()
        if solution == "0": 
            backend.SectionManager.init_section(self.system, "Menu")
            return
        player = self.system.player.sys
        enemy = self.system.environment.enemy.sys
        solution = options.get(solution)
        if solution:
            player_critical, player_damage = solution.use(enemy)
            player_log = f"You attacked using {colorama.Fore.MAGENTA}{solution.name}{colorama.Fore.RESET}, dealing {colorama.Fore.RED}{player_damage}{colorama.Fore.RESET} damage" \
                         f"{" (critical)" if player_critical else ""}"
            if player_damage == 0: player_log = f"You tried using: {colorama.Fore.MAGENTA}{solution.name}{colorama.Fore.RESET}. It is broken."
        else: player_log = "You did nothing."
        enemy_weapon = random.choices(enemy.equipped_weapons, list(abs(w.health) for w in enemy.equipped_weapons))[0]
        if (max(enemy_weapon.health - 10, 0) / enemy_weapon.max_health) * self.system.difficulty.data.get("enemy_attack_chance", 0.85) > random.uniform(0, 1): # We'll actually make it less likely for it to hit when the weapon has low health.
            enemy_critical, enemy_damage = enemy_weapon.use(player)
            enemy_log = f"Enemy attacked using {colorama.Fore.MAGENTA}{enemy_weapon.name}{colorama.Fore.RESET}, dealing {colorama.Fore.RED}{enemy_damage}{colorama.Fore.RESET} damage" \
                        f"{" (critical)" if enemy_critical else ""}"
            if enemy_damage == 0: enemy_log = f"Enemy tried using: {colorama.Fore.MAGENTA}{enemy_weapon.name}{colorama.Fore.RESET}. It is broken."
        else: enemy_log = "Enemy did nothing."
        self.log = [
            "[Remember that damage may be deflected by a amount]",
            player_log,
            enemy_log
        ]
        self.enemy_attack = self.system.environment.enemy.generate_attack()
        self.system.environment.move_on() # Move on along the story line

        self.system.player.on_update()
        self.system.environment.enemy.on_update()

        dead = (enemy.is_dead, player.is_dead)
        if dead[0]:
            backend.SectionManager.init_section(self.system, "Game.Success")
        elif dead[1]:
            backend.SectionManager.init_section(self.system, "Game.Loss")
        if any(dead):
            player._data["health"] = player.max_health
            for item in player.items:
                item._data["health"] = item.max_health
    
    def print_enemy(self) -> None:
        enemy = self.system.environment.enemy.sys
        print(f"Enemy: {colorama.Fore.RED}{enemy.name}{colorama.Fore.RESET} - level {colorama.Fore.CYAN}{enemy.level}{colorama.Fore.RESET}")
    
    def print_log(self) -> None:
        print("Log:")
        for text in self.log:
            print(f"{text}")

    def print_stats(self) -> None:
        player = self.system.player.sys
        enemy = self.system.environment.enemy.sys
        player_protection_list = list((i.health, i.max_health) for i in player.items if i.equipped and i.itype == backend.System.ItemType.SHIELD)
        enemy_protection_list = list((i.health, i.max_health) for i in enemy.items if i.equipped and i.itype == backend.System.ItemType.SHIELD)
        player_protection = (int(sum(prot[0] for prot in player_protection_list)), int(sum(prot[1] for prot in player_protection_list)))
        enemy_protection = (int(sum(prot[0] for prot in enemy_protection_list)), int(sum(prot[1] for prot in enemy_protection_list)))
        print(f"You ({colorama.Fore.GREEN}{player.name}{colorama.Fore.RESET}) have: {(colorama.Fore.GREEN if player.health > 50 else colorama.Fore.RED) + colorama.Style.BRIGHT}{player.health}{colorama.Style.RESET_ALL}{colorama.Fore.BLUE}/{colorama.Fore.RESET}{colorama.Fore.GREEN}{player.max_health}{colorama.Fore.RESET} health"
              f" ({colorama.Fore.CYAN}{max(player_protection[0], 0)}/{player_protection[1]}{colorama.Fore.RESET} protection){" (on fire)" if player.fire_damage > 0 else ""}")
        print(f"Enemy ({colorama.Fore.RED}{enemy.name}{colorama.Fore.RESET}) has: {(colorama.Fore.GREEN if enemy.health > 50 else colorama.Fore.RED) + colorama.Style.BRIGHT}{enemy.health}{colorama.Style.RESET_ALL}{colorama.Fore.BLUE}/{colorama.Fore.RESET}{colorama.Fore.GREEN}{enemy.max_health}{colorama.Fore.RESET} health"
              f" ({colorama.Fore.CYAN}{max(enemy_protection[0], 0)}/{enemy_protection[1]}{colorama.Fore.RESET} protection){" (on fire)" if enemy.fire_damage > 0 else ""}")
    
    def render_items(self) -> Dict[str, backend.System.ItemProtocol]:
        processed = {}
        for i, item in enumerate(self.system.player.sys.equipped_weapons):
            print(f"{colorama.Fore.BLUE}{i+1}{colorama.Fore.RESET}: {colorama.Fore.MAGENTA}{item.name}{colorama.Fore.RESET} [{f"{colorama.Fore.GREEN}{max(item.health, 0)}/{item.max_health}{colorama.Fore.RESET}" if item.health >= 0 else f"{colorama.Fore.RED}{abs(item.health)}{colorama.Fore.RESET}"}] - {colorama.Fore.BLUE}{item.generate_attack()}{colorama.Fore.RESET}")
            processed[str(i+1)] = item
        return processed

print("Loading... (New Objects)", end="\r")

class SectionLibrary: 
    # We create all sections and load them one by one.
    sections: Dict[str, backend.Section] = {
        "Menu": MenuSection(),
        "Settings": SettingsSection(),
        "Intel": IntelSection(),
        "Shop": ShopSection(),
        "Shop.Popup": ShopSection.Popup(),
        "Shop.Weapons": ShopSection.Weapons(),
        "Shop.Armor": ShopSection.Armor(),
        "Inventory": InventorySection(),
        "Inventory.Weapons": InventorySection.Weapons(),
        "Inventory.Armor": InventorySection.Armor(),
        "Blacksmith": BlacksmithSection(),
        "Blacksmith.Popup": BlacksmithSection.Popup(),
        "Blacksmith.Weapons": BlacksmithSection.Weapons(),
        "Blacksmith.Armor": BlacksmithSection.Armor(),
        "About": AboutSection(),
        "Documentation": DocumentationSection(),
        "Save": SaveSection(),
        "Save.Save": SaveSection.Save(),
        "Loading": LoadingSection(),
        "Game": GameSection(),
        "Game.Success": GameSection.Success(),
        "Game.Loss": GameSection.Loss()
    }

    @classmethod
    def load(cls) -> None:
        """Load all sections into the manager."""
        for name, section in cls.sections.items():
            backend.SectionManager.load_section(name, section)

SectionLibrary.load()

print("Loading... (Startng)", end="\r")

game = backend.Game()
backend.SectionManager.init_section(game, "Menu")
game.run()