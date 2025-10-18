# I'm sorry. I had some fun with this one... overcomplicating it...

from typing import Iterable, Tuple, List, Dict, Optional, Literal, Union, Self, TypeVar, overload
import colorama
import sys
import os
import re

__all__ = (
    "Terminal"
)

T = TypeVar("T", bound="Terminal.Color")

class Manager:
    class Environment:
        def __init__(self, prefix: Optional["Terminal.Color"] = None, suffix: Optional["Terminal.Color"] = None):
            self.prefix_color: Optional[Terminal.Color] = prefix
            self.suffix_color: Optional[Terminal.Color] = suffix
            self.active: bool = False

            self.last_formated: Optional[str] = None
        
        @property
        def prefix(self) -> str:
            return "" if not self.prefix_color else self.prefix_color.ansi
        
        @property
        def suffix(self) -> str:
            return "" if not self.suffix_color else self.suffix_color.ansi
        
        def __enter__(self) -> None:
            self.active = True
        
        def __exit__(self) -> None:
            self.active = False
        
        def format(self, text: str) -> str:
            self.last_formated = text # Let user know that we formated this
            return self.prefix + text + self.suffix

    def __init__(self) -> Self:
        self.env: Optional[Manager.Environment] = None
    
    @property
    def active(self) -> bool:
        return self.env and self.env.active
    
    def format(self, text: str) -> str:
        if not self.active:
            return text
        return self.env.format(text)
    
    def new_env(self, prefix: Optional["Terminal.Color"] = None, suffix: Optional["Terminal.Color"] = None) -> Environment:
        self.env = self.Environment(prefix, suffix)
        return self.env

class Terminal:
    ColorKeys: Dict[str, "Terminal.Color"] = {}
    _initialized: bool = False
    manager: Manager = Manager()
    pattern: str = r"(\$[a-z]{3})"
    
    class Color:
        """
        Represents an ANSI color sequence.
        You can construct directly, or use Color[...] lookup.
        """
        def __init__(self, *ansi: str, tag: Optional[str] = None) -> Self:
            self.ansi: str = "".join(ansi)
            self.tag: Optional[str] = tag

        @classmethod
        def lookup(cls, tag: str) -> Optional["Terminal.Color"]:
            return Terminal.lookup(tag)
        
        @classmethod
        def rgb(cls, r: int, g: int, b: int) -> "Terminal.Color":
            return cls(f"\033[38;2;{r};{g};{b}m")
        
        @classmethod
        def bg_rgb(cls, r: int, g: int, b: int) -> "Terminal.Color":
            return cls(f"\033[48;2;{r};{g};{b}m")
        
        def compare(self, other: Union["Terminal.Color", str], using: Literal["Tag","Ansi","Both"]="Ansi") -> bool:
            if isinstance(other, Terminal.Color):
                return self.ansi == other.ansi if using == "Ansi" else self.tag == other.tag if using == "Tag" else self.ansi == other.ansi and self.tag == other.tag if using == "Both" else False
            if isinstance(other, str):
                return self.ansi == other if using == "Ansi" else self.tag == other if using == "Tag" else False
            return False
        
        @classmethod
        def combine(cls, *colors_or_strings: Union["Terminal.Color", str]) -> "Terminal.Color":
            """Combine multiple colors or strings into a single Color object."""
            ansi = "".join(str(c) for c in colors_or_strings)
            return cls(ansi)
        
        def __str__(self) -> str:
            return self.ansi

        def __repr__(self) -> str:
            return f"Terminal.Color(tag={self.tag!r}, ansi={self.ansi!r})"

        def __eq__(self, other: object) -> bool:
            if isinstance(other, Terminal.Color):
                return self.ansi == other.ansi
            if isinstance(other, str):
                return self.ansi == other
            return NotImplemented

        def __add__(self, other: Union[str, "Terminal.Color", Iterable[Union[str, "Terminal.Color"]]]) -> "Terminal.Color":
            if isinstance(other, Iterable) and not isinstance(other, (str, bytes)):
                return self.combine(self, *other)
            return self.combine(self, other)

        # enable `Terminal.Color["$gre"]`
        def __class_getitem__(cls, key: Union[Tuple[Literal["Tag","ColorKey","Ansi"], str], str]) -> "Terminal.Color":
            if not Terminal._initialized:
                Terminal.colorama_init()

            if isinstance(key, str):
                if key not in Terminal.ColorKeys:
                    raise KeyError(f"Color key {value!r} not found.")
                return Terminal.ColorKeys[key]

            mode, value = key
            if mode == "Tag":
                # Return Color matching the tag if exists
                return cls(tag=value) # This is seperate from getting the colorkey
            elif mode == "ColorKey":
                if value not in Terminal.ColorKeys:
                    raise KeyError(f"Color key {value!r} not found.")
                return Terminal.ColorKeys[value]
            elif mode == "Ansi":
                return cls(value)
            raise KeyError(f"Invalid mode {mode!r} for Color lookup")
    
    class IOString: # This string is a io (input/output) string
        def __init__(self, value: str = "") -> Self:
            self.value: str = value
        
        def __str__(self) -> str:
            return self.value
        
        def input(
            self,
            *prompt: object,
            sep: Optional[str] = " ",
            end: Optional[str] = "",
            flush: bool = False,
            color: bool = False,
            clear_screen: Union[bool, Tuple[bool, bool]] = False,
            input_text: Optional[str] = None,
            n: int = -1
        ) -> None: # We may change it on input
            self.value = Terminal.input(*prompt, sep=sep, end=end, flush=flush, color=color, clear_screen=clear_screen, input_text=input_text, n=n)

        def print(
            self, 
            before: str, after: str, 
            sep: Optional[str] = " ", 
            end: Optional[str] = "\n", 
            flush: bool = False,
            color: bool = False,
            clear_screen: Union[bool, Tuple[bool, bool]] = False,
        ) -> None:
            Terminal.print(before, self, after, sep=sep, end=end, flush=flush, color=color, clear_screen=clear_screen)
    
    class AnimatedString(IOString): # This String is an animated string
        def __init__(self, frames: List[str], init: int = 0) -> Self:
            self.frames: List[str] = frames
            self.index: int = init
        
        @property
        def value(self) -> str:
            return self.frames[self.index]
        
        def __str__(self) -> str:
            return self.frames[self.index]
        
        def next(self) -> None:
            self.index += 1
            if self.index > len(self.frames) - 1:
                self.index = 0

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
                cls.Color(cls.Style.DIM, tag="$dim"),
                cls.Color(cls.Style.RESET_ALL, tag="$res")
            ]
        }
        cls._initialized = True
    
    @classmethod
    def new_env(cls, prefix: Optional["Terminal.Color"] = None, suffix: Optional["Terminal.Color"] = None) -> Manager.Environment:
        return cls.manager.new_env(prefix, suffix)
    
    @staticmethod
    def clear(ansi: bool = False) -> None:
        """Clears the screen (cross-platform)."""
        if ansi:
            sys.stdout.write("\033[2J\033[H")
            sys.stdout.flush()
        else:
            os.system("cls" if os.name == "nt" else "clear")
    
    @classmethod
    def lookup(cls, tag: str) -> Optional["Terminal.Color"]:
        if not Terminal._initialized:
            Terminal.colorama_init()
            
        if tag not in Terminal.ColorKeys:
            return None
        return Terminal.ColorKeys[tag]
    
    @classmethod
    def rgb(cls, r: int, g: int, b: int) -> "Terminal.Color":
        return cls.Color.rgb(r, g, b)
    
    @classmethod
    def bg_rgb(cls, r: int, g: int, b: int) -> "Terminal.Color":
        return cls.Color.bg_rgb(r, g, b)
    
    @classmethod
    def add_color(cls, color: "Terminal.Color", tag: Optional[str] = None) -> None:
        tag = tag or color.tag
        if tag is None:
            raise KeyError("A tag must be provided either via parameter or in the Color object")
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
        if color and not cls._initialized:
            cls.colorama_init()
        text = cls.manager.format((sep or " ").join(map(str, values)) + (end or ""))
        if not color:
            return text
        pattern = re.compile(cls.pattern)
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
        additional_prompt_text: Optional[str] = None,
        n: int = -1
    ) -> str:
        """Get input with optional formatting and clearing."""
        Terminal.print(*prompt, sep=sep, end=end, flush=flush, color=color, clear_screen=clear_screen)
        if n == -1:
            return input(additional_prompt_text)
        return sys.stdin.read(n)
    
    @classmethod
    def set_color(cls, color: "Terminal.Color") -> None:
        """Immediately set console color without newline."""
        sys.stdout.write(str(color))
        sys.stdout.flush()