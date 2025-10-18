# I'm sorry. I had some fun with this one... overcomplicating it...

from typing import Tuple, Dict, Optional, Literal, Union, Type, Self, TypeVar, overload
import colorama
import sys
import os
import re

__all__ = (
    "Terminal"
)

T = TypeVar("T", bound="Terminal.Color")

class Terminal:
    ColorKeys: Dict[str, "Terminal.Color"] = {}
    
    class Color:
        """
        Represents an ANSI color sequence.
        You can construct directly, or use Color[...] lookup.
        """
        def __init__(self, *ansi: str, tag: Optional[str] = None) -> Self:
            self.ansi: str = "".join(ansi)
            self.tag: Optional[str] = tag
        
        @classmethod
        def rgb(cls, r: int, g: int, b: int) -> "Terminal.Color":
            return cls(f"\033[38;2;{r};{g};{b}m")
        
        @classmethod
        def bg_rgb(cls, r: int, g: int, b: int) -> "Terminal.Color":
            return cls(f"\033[48;2;{r};{g};{b}m")
        
        def compare(self, other: Union["Terminal.Color", str], using: Literal["Tag","Ansi"]="Ansi") -> bool:
            if isinstance(other, Terminal.Color):
                return self.ansi == other.ansi if using == "Ansi" else self.tag == other.tag
            if isinstance(other, str):
                return self.ansi == other if using == "Ansi" else self.tag == other
            return False
        
        def __str__(self) -> str:
            return self.ansi

        def __repr__(self) -> str:
            return f"Terminal.Color({repr(self.ansi)})"

        def __eq__(self, other: object) -> bool:
            if isinstance(other, Terminal.Color):
                return self.ansi == other.ansi
            if isinstance(other, str):
                return self.ansi == other
            return NotImplemented

        def __add__(self, other: Union[str, "Terminal.Color"]) -> "Terminal.Color":
            """Allow concatenation with other colors or strings."""
            if isinstance(other, Terminal.Color):
                return Terminal.Color(self.ansi + other.ansi)
            return Terminal.Color(self.ansi + str(other))

        # enable `Terminal.Color["$gre"]`
        def __class_getitem__(cls, key: Tuple[Literal["Tag","ColorKey","Ansi"], str]) -> "Terminal.Color":
            mode, value = key
            if not Terminal.ColorKeys:
                Terminal.colorama_init()

            if mode == "Tag":
                # Return Color matching the tag if exists
                return Terminal.ColorKeys.get(value, cls(tag=value))
            elif mode == "ColorKey":
                if value not in Terminal.ColorKeys:
                    raise KeyError(f"Color key {value!r} not found.")
                return Terminal.ColorKeys[value]
            elif mode == "Ansi":
                return cls(value)
            raise KeyError(f"Invalid mode {mode!r} for Color lookup")

    @classmethod
    def colorama_init(cls) -> None:
        colorama.init()
        cls.Fore = colorama.Fore
        cls.Style = colorama.Style
        cls.Back = colorama.Back
        cls.ColorKeys = {
            i.tag: i for i in [
                cls.Color(cls.Fore.BLACK, tag="$bla"),
                cls.Color(cls.Fore.BLUE, tag="$blu"),
                cls.Color(cls.Fore.CYAN, tag="$cya"),
                cls.Color(cls.Fore.GREEN, tag="$gre"),
                cls.Color(cls.Fore.MAGENTA, tag="$mag"),
                cls.Color(cls.Fore.RED, tag="$red"),
                cls.Color(cls.Fore.WHITE, tag="$whi"),
                cls.Color(cls.Fore.YELLOW, tag="$yel"),
                cls.Color(cls.Style.BRIGHT, tag="$bri"),
                cls.Color(cls.Style.DIM, "$dim"),
                cls.Color(cls.Style.RESET_ALL, tag="$res")
            ]
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
    def rgb(cls, r: int, g: int, b: int) -> "Terminal.Color":
        return cls.Color.rgb(r, g, b)
    
    @classmethod
    def bg_rgb(cls, r: int, g: int, b: int) -> "Terminal.Color":
        return cls.Color.bg_rgb(r, g, b)

    @classmethod
    def add_color(cls, tag: str, color: "Terminal.Color") -> None:
        """Add a custom color key (ex: '$err', Color(Back.RED, Style.BRIGHT))"""
        cls.ColorKeys[tag] = color
    
    @overload
    @classmethod
    def pop_color(cls, tag: str, /) -> str:
        ...
    
    @overload
    @classmethod
    def pop_color(cls, tag: str, default: Optional["Terminal.Color"], /) -> str:
        ...
    
    @classmethod
    def pop_color(cls, tag: str, default: Optional["Terminal.Color"] = None) -> str:
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
        text = Terminal.format(formatted_string, end=end, color=color)
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
    
    @classmethod
    def set_color(cls, color: "Terminal.Color") -> None:
        """Immediately set console color without newline."""
        sys.stdout.write(str(color))
        sys.stdout.flush()