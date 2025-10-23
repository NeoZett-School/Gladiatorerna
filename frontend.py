# What we can see on screen
import Terminal

Terminal.print("Loading... (Bootup)", end="\r")

from typing import Tuple, List, Dict, Optional, Self, Any
from items import ItemLibrary # Import the item library
import backend # Import the backend
import datetime
import random
import time
import os
import re

if not __name__ == "__main__":
    exit() # If this file was not run directly, we can simply exit like normal before anything get run.

Terminal.init() # Initialize the terminal (including colorama)

Terminal.print("Loading... (Creating Objects)", end="\r")

class MenuSection(backend.Section): # We create a section for the menu
    def on_render(self) -> None: # On every render, we do...
        Terminal.print(f"Welcome to $cya$briGladiatorerna$res!", color=True)
        if not self.system.player:
            Terminal.space()
            Terminal.print("$briBefore$res you $greStart$res, check that you have chosen your character in the $cyaSettings$res."
                           "\nThe $magShop$res and $cyaInventory$res will be unlocked once you've started the game and your character "
                           "\nhas been chosen. Once you have started, you can go back and buy new gear."
                           "\nTo do this, open the store. Then, you can go back into the battlefield, selecting $greStart$res.", color=True)
        Terminal.space()
        Terminal.print(f"Current time is: $yel{datetime.datetime.now().strftime("%H:%M")}$res", color=True)
        Terminal.space()
        Terminal.print("Where would you like to go?")
        options = {
            # id, title, section
            "1": (Terminal.format("$greStart$res"), "Game"),
            "2": (Terminal.format("$cyaSaves$res"), "Save"),
            "3": (Terminal.format("$bluAbout$res"), "About"),
            "4": (Terminal.format("$yelDocumentation$res"), "Documentation"),
            "5": (Terminal.format("$cyaSettings$res"), "Settings"),
            "6": (Terminal.format("$yelIntel$res"), "Intel")
        }
        exit_id = "7"
        if self.system.player: # If the game has initialized, we can safely reveal the shop!
            options["7"] = (Terminal.format("$magShop$res"), "Shop")
            options["8"] = (Terminal.format("$bluBlacksmith$res"), "Blacksmith")
            options["9"] = (Terminal.format("$cya$briInventory$res"), "Inventory")
            exit_id = "10"
        options[exit_id] = (Terminal.format("$redExit$res"), "Exit")
        options_string = ""
        for k, v in options.items():
            options_string += f"$blu{k}$res: {v[0]}\n"
        Terminal.print(options_string[:-1], color=True)
        solution = options.get(Terminal.input("Select one $bluoption$res: ", color=True).lower().strip())
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
        Terminal.print("Options:")
        options = {
            # id, title, current value
            "1": ("Difficulty", self.system.difficulty.name),
        }
        if not self.system.player:
            options["2"] = ("Character", self.system.char_name)
        Terminal.print(f"$red0$res: Go back", color=True)
        options_string = ""
        for k, v in options.items():
            options_string += f"$blu{k}$res: $yel{v[0]}$res [$mag{v[1]}$res]\n"
        Terminal.print(options_string[:-1], color=True)
        solution = Terminal.input("Select one $blusetting$res to $yelchange$res: ", color=True).lower().strip()
        if solution == "0": 
            backend.SectionManager.init_section(self.system, "Menu")
            return
        solution = options.get(solution)
        if not solution: return
        Terminal.space()
        match solution[0]:
            case "Difficulty":
                Terminal.print("Difficulties:")
                for name, difficulty in backend.Difficulty.__members__.items():
                    Terminal.print(f"$mag{name}$res - $blu{difficulty.data.get("desc", "No description available.")}$res", color=True)
                if self.system.player:
                    Terminal.print("[The new difficulty only apply once a new battle begins]")
                new_difficulty = None
                while not new_difficulty:
                    new_difficulty = backend.Difficulty.get(Terminal.input("Select one $bludifficulty$res: ", color=True))
                    if not new_difficulty: Terminal.print(f"$redInvalid$res. Try again.", color=True)
                self.system.difficulty = new_difficulty
            case "Character":
                Terminal.print("Characters:")
                for name, data in backend.CONFIG.characters.items():
                    Terminal.print(f"$mag{name}$res - $blu{data.get("desc", "No description available.")}$res", color=True)
                new_character = None
                while not new_character:
                    new_character = Terminal.input("Select one character: ")
                    if not new_character in backend.CONFIG.characters: 
                        Terminal.print(f"$redInvalid$res. Try again.", color=True)
                        new_character = None
                self.system.char_name = new_character

class ShopSection(backend.Section):
    class Popup(backend.Section):
        def init(self) -> None:
            super().init()
            self.shop: "ShopSection" = SectionLibrary.sections["Shop"]
        
        def on_render(self) -> None:
            item = self.shop.to_buy
            options = {
                # id, title, code
                "1": (Terminal.format("$gre$briYes$res"), "Y"),
                "2": (Terminal.format("$red$briNo$res"), "N")
            }
            Terminal.print(f"Are you sure you want to buy $mag$bri{item.name}$res?", color=True)
            options_string = ""
            for k, v in options.items():
                options_string += f"$blu{k}$res: {v[0]}\n"
            Terminal.print(options_string[:-1], color=True)
            solution = options.get(Terminal.input("Select one $bluoption$res: ", color=True).lower().strip())
            if not solution: return
            if solution[1] == "Y":
                if not item.buy(self.system.player.sys):
                    Terminal.print("You can't buy this item.")
                    Terminal.input("Press enter to continue...")
            backend.SectionManager.init_section(self.system, "Shop")

    class Directory(backend.Section):
        items: List[Tuple[str, backend.System.ItemProtocol]]

        def init(self) -> None:
            super().init()
            self.shop: "ShopSection" = SectionLibrary.sections["Shop"]

        def on_render(self) -> None:
            self.shop.render_title()
            points = int(self.system.player.sys.points)
            Terminal.print("")
            self.shop.render_points(points)
            self.shop.render_count(len(self.items))
            Terminal.print("")
            Terminal.print("$red0$res: Go back", color=True)
            options = self.shop.render_items(points, self.items)
            solution = Terminal.input("Select one item you want to $blubuy$res: ", color=True).lower().strip()
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
        if not self.system.player: # We are not initialized yet!
            backend.SectionManager.init_section(self.system, "Menu")
            return

        self.render_title()
        Terminal.space()
        self.render_points(int(self.system.player.sys.points))
        self.render_count(len(self.items))
        Terminal.space()
        options = {
            # id, title, section
            "1": (Terminal.format("$redWeapons$res"), "Shop.Weapons"),
            "2": (Terminal.format("$greArmor$res"), "Shop.Armor")
        }
        Terminal.print("$red0$res: Go back", color=True)
        options_string = ""
        for k, v in options.items():
            options_string += f"$blu{k}$res: {v[0]}\n"
        Terminal.print(options_string[:-1], color=True)
        solution = Terminal.input("Select one $bludirectory$res: ", color=True).lower().strip()
        if solution == "0": 
            backend.SectionManager.init_section(self.system, "Menu")
            return
        solution = options.get(solution)
        if not solution: return
        backend.SectionManager.init_section(self.system, solution[1])

    def render_title(self) -> None:
        Terminal.print("---- {$gre$briSHOP$res} ----", color=True)
    
    def render_points(self, points: int) -> None:
        Terminal.print(f"Your points: $yel$bri{points}p$res", color=True)
    
    def render_count(self, count: int) -> None:
        Terminal.print(f"Items for sale: $blu{count}$res", color=True)
    
    def render_items(self, points: int, items: List[backend.System.ItemProtocol]) -> Dict[str, backend.System.ItemProtocol]:
        processed = {}
        options_string = ""
        for i, item in enumerate(items):
            if item.owned or not item.minimal_level <= self.system.player.sys.level: continue
            options_string += f"$blu{i+1}$res: $mag{item.name}$res [{("$gre" if points >= item.cost else "$red") + "$bri"}{item.cost}p$res] - $blu{item.desc}$res\n"
            processed[str(i+1)] = item
        Terminal.print(options_string[:-1], color=True)
        return processed

class InventorySection(backend.Section):
    class Directory(backend.Section):
        items: List[Tuple[str, backend.System.ItemProtocol]]

        def init(self) -> None:
            super().init()
            self.inv: "InventorySection" = SectionLibrary.sections["Inventory"]

        def on_render(self) -> None:
            self.inv.render_title()
            Terminal.space()
            self.inv.render_count(len(self.items))
            Terminal.space()
            Terminal.print(f"$red0$res: Go back", color=True)
            options = self.inv.render_items(self.items)
            solution = Terminal.input("Select one item you want to $bluchange$res: ", color=True).lower().strip()
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
        if not self.system.player: # We are not initialized yet!
            backend.SectionManager.init_section(self.system, "Menu")
            return

        self.render_title()
        Terminal.space()
        self.render_count(len(self.system.player.sys.items))
        Terminal.space()
        options = {
            # id, title, section
            "1": (Terminal.format("$redWeapons$res"), "Inventory.Weapons"),
            "2": (Terminal.format("$greArmor$res"), "Inventory.Armor")
        }
        Terminal.print("$red0$res: Go back", color=True)
        options_string = ""
        for k, v in options.items():
            options_string += f"$blu{k}$res: {v[0]}\n"
        Terminal.print(options_string[:-1], color=True)
        solution = Terminal.input("Select one $bludirectory$res: ", color=True).lower().strip()
        if solution == "0": 
            backend.SectionManager.init_section(self.system, "Menu")
            return
        solution = options.get(solution)
        if not solution: return
        backend.SectionManager.init_section(self.system, solution[1])

    def render_title(self) -> None:
        Terminal.print("---- {$cya$briInventory$res} ----", color=True)
    
    def render_count(self, count: int) -> None:
        Terminal.print(f"Your items: $yel$bri{count}$res", color=True)

    def render_items(self, items: List[Tuple[str, backend.System.ItemProtocol]]) -> Dict[str, backend.System.ItemProtocol]:
        processed = {}
        options_string = ""
        for i, (name, item) in enumerate(items):
            if not item.owned: continue
            options_string += f"$blu{i+1}$res: $mag{name}$res [{("$gre" if item.equipped else "$red") + "$bri"}{"Equipped" if item.equipped else "Unequipped"}$res] - $blu{item.desc}$res\n"
            processed[str(i+1)] = item
        Terminal.print(options_string[:-1], color=True)
        return processed

class IntelSection(backend.Section):
    def on_render(self) -> None:

        # Items
        Terminal.print("Items:")
        def print_items(items: List[backend.System.ItemProtocol]) -> None:
            for item in items:
                if self.system.player:
                    owned = item in self.system.player.sys.items and item.owner == self.system.player.sys
                Terminal.print(f"$mag{item.name}$res"
                    f"{f" ($yel{item.upgrades}$res)" \
                    f" [{("$gre" if item.equipped and owned else "$red") + "$bri"}{"Equipped" if item.equipped else "Unequipped" if owned else "Not owned"}$res]" if self.system.player else ""}" 
                    f" - $blu{item.desc}$res", color=True)
                separator = f"\n$blu - $yel"
                intel_raw = str(item.intel)  # Ensure it's a string

                # Function to color digits
                def color_numbers(text):
                    # Match integers or floats (e.g., 12, 0.45, 123.456)
                    pattern = r'\b\d+(?:\.\d+)?\b'
                    return re.sub(pattern, lambda m: f"$blu{m.group(0)}$yel", text)

                # Build the formatted string
                intel_text = f"$yel{separator[1:]}{color_numbers(intel_raw)}$res\n"

                # Apply the separator formatting
                formatted_output = separator.join(intel_text.split(", "))
                Terminal.print(formatted_output, color=True)
        if self.system.player:
            print_items(self.system.player.inventory.items)
        else: print_items(list(i() for i in ItemLibrary.items))
        
        # Stats
        Terminal.space()
        Terminal.print("Players:")
        if self.system.player:
            player = self.system.player.sys
            Terminal.print(f"-- $yel{player.name}$res --", color=True)
            Terminal.print("$mag[ YOU ]$res", color=True)
            items = {
                # Title, value
                "Points": f"{int(player.points)}p",
                "Level": f"{player.level}",
                "Exp": f"{Terminal.progress_bar("$yel[has]$blu[need]$res", has=player.exp, need=1.0)} ({int(player.exp*100)}%)",
                "Max Health": f"{player.max_health}",
                "Healing": f"{player.healing} seconds/hp",
                "Base Attack": f"{player.base_attack}",
                "Protection": f"{int(sum(i.max_health for i in player.items if i.equipped and i.itype == backend.System.ItemType.SHIELD))}",
                "Critical Chance": f"{player.critical_chance}",
                "Critical Factor": f"{player.critical_factor}"
            }
            stats_string = ""
            for title, value in items.items():
                stats_string += f"$yel{title}$res: $blu{value}$res\n"
            Terminal.print(stats_string, color=True)
        
        for name, data in backend.CONFIG.characters.items():
            if self.system.player and self.system.player.sys.name == name: continue
            Terminal.print(f"-- $yel{name}$res --", color=True)
            items = {
                # Title, value
                "Max Health": f"{data["max_health"]}",
                "Healing": f"{data["healing"]} seconds/hp",
                "Base Attack": f"{data["base_attack"]}",
                "Critical Chance": f"{data["critical_chance"]}",
                "Critical Factor": f"{data["critical_factor"]}"
            }
            stats_string = ""
            for title, value in items.items():
                stats_string += f"$yel{title}$res: $blu{value}$res\n"
            Terminal.print(stats_string, color=True)
            
        Terminal.space()
        Terminal.print("$red0$res: Go back", color=True)
        solution = Terminal.input("Select one $bluoption$res: ", color=True).lower().strip()
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
                "1": (Terminal.format("$gre$briYes$res"), "Y"),
                "2": (Terminal.format("$red$briNo$res"), "N")
            }
            Terminal.print(f"Are you sure you want to upgrade $mag$bri{item.name}$res?", color=True)
            options_string = ""
            for k, v in options.items():
                options_string += f"$blu{k}$res: {v[0]}\n"
            Terminal.print(options_string[:-1], color=True)
            solution = options.get(Terminal.input("Select one $bluoption$res: ", color=True).lower().strip())
            if not solution: return
            if solution[1] == "Y":
                if not item.upgrade():
                    Terminal.print("You can't upgrade this item.")
                    Terminal.input("Press enter to continue...")
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
            Terminal.space()
            self.blacksmith.render_points(points)
            self.blacksmith.render_count(len(self.items))
            Terminal.space()
            Terminal.print("$red0$res: Go back", color=True)
            options = self.blacksmith.render_items(points, self.items)
            solution = Terminal.input("Select one item you want to $bluupgrade$res: ", color=True).lower().strip()
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
        if not self.system.player: # We are not initialized yet!
            backend.SectionManager.init_section(self.system, "Menu")
            return

        self.render_title()
        Terminal.space()
        self.render_points(int(self.system.player.sys.points))
        self.render_count(len(self.items))
        Terminal.space()
        options = {
            # id, title, section
            "1": (Terminal.format("$redWeapons$res"), "Blacksmith.Weapons"),
            "2": (Terminal.format("$greArmor$res"), "Blacksmith.Armor")
        }
        Terminal.print(f"$red0$res: Go back", color=True)
        options_string = ""
        for k, v in options.items():
            options_string += f"$blu{k}$res: {v[0]}\n"
        Terminal.print(options_string[:-1], color=True)
        solution = Terminal.input("Select one $bludirectory$res: ", color=True).lower().strip()
        if solution == "0": 
            backend.SectionManager.init_section(self.system, "Menu")
            return
        solution = options.get(solution)
        if not solution: return
        backend.SectionManager.init_section(self.system, solution[1])

    def render_title(self) -> None:
        Terminal.print("---- {$gre$briBLACKSMITH$res} ----", color=True)
    
    def render_points(self, points: int) -> None:
        Terminal.print(f"Your points: $yel$bri{points}p$res", color=True)
    
    def render_count(self, count: int) -> None:
        Terminal.print(f"Items for upgrade: $blu{count}$res", color=True)
    
    def render_items(self, points: int, items: List[Tuple[str, backend.System.ItemProtocol]]) -> Dict[str, backend.System.ItemProtocol]:
        processed = {}
        options_string = ""
        for i, (name, item) in enumerate(items):
            if not item.owned: continue
            options_string += f"$blu{i+1}$res: $mag{name}$res [{("$gre" if points >= item.upgrade_cost else "$red") + "$bri"}{item.upgrade_cost}p$res] - $blu{item.desc}$res\n"
            processed[str(i+1)] = item
        Terminal.print(options_string[:-1], color=True)
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
        return f"$redPage {self.index} not found.$res"
    
    def on_render(self) -> None:
        for text in self.page:
            Terminal.print(text, color=True)
        Terminal.space()
        Terminal.print("$red0$res: Go back", color=True)
        Terminal.print("$blu1$res: Next page", color=True)
        solution = Terminal.input("Select one $bluoption$res: ", color=True).lower().strip()
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
            return f"$gre{line}$res", citation

        # Blank lines reset citation mode
        elif stripped == "":
            citation = False
            return line, citation

        # Headings (lines starting with '#')
        if line.startswith("#"):
            return f"$cya$bri{line}$res", citation

        # Bullet points
        if line.lstrip().startswith("- "):
            content = line.lstrip().removeprefix("- ").strip()
            return f"$yel- $blu{content}$res", citation

        # Inline reset markers
        line = line.replace("$$", "$res")

        # --- Inline citations (segments between quotes) ---
        # Replace quoted segments with yellow color
        def colorize_quotes(match):
            inner = match.group(1)
            return f'$yel"{inner}"$whi'

        # Apply inline quote highlighting only if there are quote pairs
        if '"' in line:
            # Add base color first to ensure resets work cleanly
            line = "$whi" + re.sub(r'"(.*?)"', colorize_quotes, line) + "$res"
        else:
            # If currently inside a multi-line citation, keep yellow
            if citation:
                line = f"$blu$bri{line}$res"
            else:
                line = f"$whi{line}$res"

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
        return f"$redPage {self.index} not found.$res"
    
    def on_render(self) -> None:
        for text in self.page:
            Terminal.print(text, color=True)
        Terminal.space()
        Terminal.print("$red0$res: Go back", color=True)
        Terminal.print("$blu1$res: Next page", color=True)
        solution = Terminal.input("Select one $bluoption$res: ", color=True).lower().strip()
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
            Terminal.print("$cya$bri< NEW SAVE FILE >$res", color=True)
            file = Terminal.input("Input a $yelname$res for this $magfile$res: ", color=True).strip()
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
        Terminal.print("---- {$cyaSAVE FILES$res} ----", color=True)
        Terminal.space()
        if self.system.player: Terminal.print("$blu1$res: Save", color=True)
        options = self.render_saves()
        options_string = ""
        for k, v in options.items():
            options_string += f"$blu{k}$res: $yel{v[0]}$res\n"
        Terminal.print(options_string[:-1], color=True)
        Terminal.print(f"$red0$res: Go back",color=True)
        solution = Terminal.input("Select one $bluoption$res: ", color=True).lower().strip()
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
        self.symbol: Terminal.AnimatedString = Terminal.AnimatedString(["-","\\","|","/","-"])
        self.loading_bar: Terminal.ProgressBar = Terminal.ProgressBar("$gre$bri[has]$yel$dim[need]$res", "-", 10)

        self.text = ""
    
    def on_update(self) -> None:
        self.frames += 1
        if self.frames % 5 == 0: # Performance!
            current_time = time.monotonic()
            if current_time >= self.next_prog:
                self.next_prog = current_time + self.interval
                self.progress()
            if self.progression % 4 == 0:
                self.symbol.next()
            self.text = \
                f"\r$yelBringing life to your gladiators... please wait. " \
                f"$cyaLoading:$res " \
                f"$gre$bri{self.progression}% " \
                f"$blu$dim{self.symbol}$res " \
                f"[{self.loading_bar.get_frame(self.loading_bar.calc_index(self.progression, 100))}]"

    def on_render(self) -> None:
        Terminal.print(
            self.text, color=True
        )

    def progress(self) -> None:
        self.progression += 1
        if self.progression > 100:
            backend.SectionManager.init_section(self.system, "Game")

class GameSection(backend.Section):
    class Directory(backend.Section):
        title: str
        rewards: Dict[str, Any]
        loss: bool = False
        def on_render(self) -> None:
            Terminal.print(self.title, color=True)
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
                    Terminal.print(f"$yel{reward}$res $gre$bri+{amount}$res", color=True)
                else:Terminal.print(f"$yel{reward}$res $red$bri-{abs(amount)}$res", color=True)
            Terminal.space()
            options = {
                # id, title, code
                "1": (Terminal.format("$gre$briYes$res"), "Y"),
                "2": (Terminal.format("$red$briNo$res"), "N")
            }
            Terminal.print("Do you want to fight again? Otherwise return to menu.")
            for k, v in options.items():
                Terminal.print(f"$blu{k}$res: {v[0]}", color=True)
            solution = options.get(Terminal.input("Select one $bluoption$res: ", color=True).lower().strip())
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
        title = "$greSuccess$res! You won rewards: "
        def init(self) -> None:
            super().init()
            self.rewards = self.system.environment.rewards
    
    class Loss(Directory):
        title = "Oh no! You $redlost$res rewards: "
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
        Terminal.print("---- {$cya$briGLADIATORERNA$res} ----", color=True)
        Terminal.space()
        self.print_enemy()
        Terminal.print(f"Round: $gre{self.system.environment.round}$res", color=True)
        if self.log:
            Terminal.space()
            self.print_log()
        Terminal.space()
        self.print_stats()
        Terminal.space()
        Terminal.print(f"$yel$bri{self.system.environment.next}$res", color=True)
        Terminal.space()
        Terminal.print(self.enemy_attack)
        Terminal.space()
        Terminal.print("What do you do?")
        options = self.render_items()
        Terminal.print("$red0$res: Go back", color=True)
        solution = Terminal.input("Select one $bluoption$res: ", color=True).lower().strip()
        if solution == "0": 
            backend.SectionManager.init_section(self.system, "Menu")
            return
        player = self.system.player.sys
        enemy = self.system.environment.enemy.sys
        solution = options.get(solution)
        if solution:
            player_critical, player_damage = solution.use(enemy)
            player_log = Terminal.format(f"You attacked using $mag{solution.name}$res, dealing $red{player_damage}$res damage" \
                         f"{" (critical)" if player_critical else ""}")
            if player_damage == 0: 
                player_log = Terminal.format(f"You tried using: $mag{solution.name}$res. It is broken.")
        else: player_log = "You did nothing."
        enemy_weapon = random.choices(enemy.equipped_weapons, list(max(abs(w.health), 1) for w in enemy.equipped_weapons))[0]
        if max((max(enemy_weapon.health - 10, 0) / enemy_weapon.max_health) * self.system.difficulty.data.get("enemy_attack_chance", 0.85), 0.15) > random.uniform(0, 1): # We'll actually make it less likely for it to hit when the weapon has low health.
            enemy_critical, enemy_damage = enemy_weapon.use(player)
            enemy_log = Terminal.format(f"Enemy attacked using $mag{enemy_weapon.name}$res, dealing $red{enemy_damage}$res damage" \
                        f"{" (critical)" if enemy_critical else ""}")
            if enemy_damage == 0: 
                enemy_log = Terminal.format(f"Enemy tried using: $mag{enemy_weapon.name}$res. It is broken.")
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
        Terminal.print(f"Enemy: $red{enemy.name}$res - level $cya{enemy.level}$res", color=True)
    
    def print_log(self) -> None:
        Terminal.print("Log:")
        for text in self.log:
            Terminal.print(f"{text}")

    def print_stats(self) -> None:
        player = self.system.player.sys
        enemy = self.system.environment.enemy.sys
        player_protection_list = list((i.health, i.max_health) for i in player.items if i.equipped and i.itype == backend.System.ItemType.SHIELD)
        enemy_protection_list = list((i.health, i.max_health) for i in enemy.items if i.equipped and i.itype == backend.System.ItemType.SHIELD)
        player_protection = (int(sum(prot[0] for prot in player_protection_list)), int(sum(prot[1] for prot in player_protection_list)))
        enemy_protection = (int(sum(prot[0] for prot in enemy_protection_list)), int(sum(prot[1] for prot in enemy_protection_list)))
        Terminal.print(f"You ($gre{player.name}$res) have: {("$gre" if player.health > 50 else "$red") + "$bri"}{player.health}$res$blu/$res$gre{player.max_health}$res health"
              f" ($cya{max(player_protection[0], 0)}/{player_protection[1]}$res protection){" (on fire)" if player.fire_damage > 0 else ""}", color=True)
        Terminal.print(f"Enemy ($red{enemy.name}$res) has: {("$gre" if enemy.health > 50 else "$red") + "$bri"}{enemy.health}$bri$blu/$res$gre{enemy.max_health}$res health"
              f" ($cya{max(enemy_protection[0], 0)}/{enemy_protection[1]}$res protection){" (on fire)" if enemy.fire_damage > 0 else ""}", color=True)
    
    def render_items(self) -> Dict[str, backend.System.ItemProtocol]:
        processed = {}
        options_string = ""
        for i, item in enumerate(self.system.player.sys.equipped_weapons):
            options_string += f"$blu{i+1}$res: $mag{item.name}$res [{f"$gre{max(item.health, 0)}/{item.max_health}$res" if item.health >= 0 else f"$red{abs(item.health)}$res"}] - $blu{item.generate_attack()}$res\n"
            processed[str(i+1)] = item
        Terminal.print(options_string[:-1], color=True)
        return processed

Terminal.print("Loading... (New Objects)", end="\r")

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

Terminal.print("Loading... (Startng)", end="\r")

game = backend.Game()
backend.SectionManager.init_section(game, "Menu")
game.run()