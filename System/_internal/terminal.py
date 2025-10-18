# I'm sorry. I had some fun with this one... overcomplicating it...

from typing import Tuple, Dict, Optional, Literal, Union, overload
import colorama
import sys
import os
import re

__all__ = (
    "Terminal"
)

class Terminal:
    ColorKeys: Dict[str, str] = {}

    @classmethod
    def colorama_init(cls) -> None:
        colorama.init()
        cls.Fore = colorama.Fore
        cls.Style = colorama.Style
        cls.Back = colorama.Back
        cls.ColorKeys = {
            "$bla": cls.Fore.BLACK,
            "$blu": cls.Fore.BLUE,
            "$cya": cls.Fore.CYAN,
            "$gre": cls.Fore.GREEN,
            "$mag": cls.Fore.MAGENTA,
            "$red": cls.Fore.RED,
            "$whi": cls.Fore.WHITE,
            "$yel": cls.Fore.YELLOW,
            "$bri": cls.Style.BRIGHT,
            "$dim": cls.Style.DIM,
            "$res": cls.Style.RESET_ALL,
        }
    
    @staticmethod
    def clear(ansi: bool = False) -> None:
        """Clears the screen (cross-platform)."""
        if ansi:
            sys.stdout.write("\033[2J\033[H")
            sys.stdout.flush()
        else:
            os.system("cls" if os.name == "nt" else "clear")

    @classmethod
    def add_color(cls, tag: str, code: str) -> None:
        cls.ColorKeys[tag] = code
    
    @overload
    @classmethod
    def pop_color(cls, tag: str, /) -> str:
        ...
    
    @overload
    @classmethod
    def pop_color(cls, tag: str, default: str, /) -> str:
        ...
    
    @classmethod
    def pop_color(cls, tag: str, default: str) -> str:
        return cls.ColorKeys.pop(tag, default)
    
    @classmethod
    def format(
        cls, *values: object,
        sep: Optional[str] = " ", end: Optional[str] = "",
        color: bool = True
    ) -> str:
        if color and not cls.ColorKeys:
            cls.colorama_init()
        text = (sep or " ").join(map(str, values)) + (end or "")
        if not color:
            return text
        pattern = re.compile(r"(\$[a-z]{3})")
        return pattern.sub(lambda m: cls.ColorKeys.get(m.group(0), m.group(0)), text)
    
    @staticmethod
    def progress_bar(
        formatted_string: str = "[had]|[need]",
        token: str = "-", length: int = 10,
        has: float = 0, need: float = 10,
        end: Optional[str] = "", color: bool = True
    ) -> str:
        text = Terminal.format(formatted_string, color=color)
        factor = has / need if need else 0
        progress = int(length * factor)
        return text.replace("[has]", token * progress).replace("[need]", token * (length - progress))
    
    @staticmethod
    def print(
        *values: object,
        sep: Optional[str] = " ",
        end: Optional[str] = "\n",
        flush: bool = False,
        color: bool = False,
        clear_screen: Union[bool, Tuple[bool, bool]] = False
    ) -> None:
        """Print the given values onto the screen."""
        if clear_screen:
            if isinstance(clear_screen, tuple) and clear_screen[0]:
                Terminal.clear(clear_screen[1])
            elif isinstance(clear_screen, bool):
                Terminal.clear(False)

        text = Terminal.format(*values, sep=sep, end=end, color=color)
        sys.stdout.write(text)
        if flush:
            sys.stdout.flush()
    
    @staticmethod
    def input(
        *prompt: object,
        sep: Optional[str] = " ",
        end: Optional[str] = "",
        flush: bool = False,
        color: bool = False,
        clear_screen: Union[bool, Tuple[bool, bool]] = False,
        input_text: Optional[str] = None,
        n: int = -1
    ) -> str:
        """Get input with optional formatting and clearing."""
        Terminal.print(*prompt, sep=sep, end=end, flush=flush, color=color, clear_screen=clear_screen)
        if n == -1:
            return input(input_text)
        return sys.stdin.read(n)