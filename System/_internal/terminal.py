# I'm sorry. I had some fun with this one... overcomplicating it...

from typing import Iterable, Tuple, List, Dict, Optional, Callable, Literal, Union, Self, TypeVar, Any, overload
import colorama
import sys
import os
import re

__all__ = ("Terminal",)

T = TypeVar("T", bound="Terminal.Color")
ClearScreenArg = Union[bool, Tuple[bool, bool], Tuple[bool, bool, bool]]

class Manager:
    class Environment:
        class GlobalInterface: 
            """Public interface for an active environment context."""

            def __init__(self, env: "Manager.Environment") -> Self:
                self._env: Manager.Environment = env
            
            @property
            def active(self) -> bool:
                return self._env.active
            
            @property
            def prefix(self) -> "Terminal.Color":
                return self._env.prefix_color
            
            @property
            def suffix(self) -> "Terminal.Color":
                return self._env.suffix_color
            
            @property
            def formatted(self) -> List[str]:
                return self._env.formatted[:]
            
            def format(self, text: str) -> str:
                return self._env.format(text)
            
            def disable(self) -> None:
                self._env.disable()

        def __init__(
            self, 
            manager: "Manager", 
            prefix: Optional["Terminal.Color"] = None, 
            suffix: Optional["Terminal.Color"] = None
        ) -> Self:
            self.manager: Manager = manager
            self.prefix_color: Optional[Terminal.Color] = prefix
            self.suffix_color: Optional[Terminal.Color] = suffix
            self.active: bool = False
            self.formatted: List[str] = []
        
        @property
        def prefix(self) -> str:
            return self.prefix_color.ansi if self.prefix_color else ""
        
        @property
        def suffix(self) -> str:
            return self.suffix_color.ansi if self.suffix_color else ""
        
        def enable(self) -> GlobalInterface:
            if not self in self.manager.env_stack:
                self.manager.env_stack.append(self)
            self.active = True
            return self.GlobalInterface(self)
        
        def disable(self) -> None:
            if self in self.manager.env_stack:
                self.manager.env_stack.remove(self)
            self.active = False
        
        def __enter__(self) -> GlobalInterface:
            return self.enable()
        
        def __exit__(self, *args) -> None:
            self.disable()
        
        def format(self, text: str) -> str:
            self.formatted.append(text)
            return self.prefix + text + self.suffix

    def __init__(self) -> Self:
        self.env_stack: List[Manager.Environment] = []
        self.mode: Literal["Single", "Multiple"] = "Single"
    
    @property
    def active(self) -> bool:
        return any(env.active for env in self.env_stack)
    
    def disable(self) -> None:
        """Disable all active environments."""
        while self.env_stack:
            env = self.env_stack.pop()
            env.active = False
    
    def format(self, text: str) -> str:
        """Apply formatting from the latest active environment. (Depends on mode)"""
        if not self.active:
            return text
        match self.mode:
            case "Single":
                index = -1
                while self.env_stack[index].active == False:
                    index -= 1
                text = self.env_stack[index].format(text)
            case "Multiple":
                for env in self.env_stack:
                    if not env.active: continue
                    text = env.format(text)
        return text
    
    def new_env(self, prefix: Optional["Terminal.Color"] = None, suffix: Optional["Terminal.Color"] = None) -> Environment:
        """Create a new environment."""
        env = self.Environment(self, prefix, suffix)
        self.env_stack.append(env)
        return env

class Terminal:
    """A flexible terminal interface with colors, formatting, and environment stacks."""

    ColorKeys: Dict[str, "Terminal.Color"] = {}
    manager: Manager = Manager()
    pattern: str = r"(\$[a-z]{3})"
    _initialized: bool = False
    _regex: Optional[re.Pattern] = None

    class Simple:
        """Disconnected, minimal terminal I/O."""

        @staticmethod
        def space() -> None:
            """Simple print a space in the terminal."""
            sys.stdout.write("\n")
        
        @staticmethod
        def print(*values: object, sep: Optional[str] = " ", end: Optional[str] = "\n", flush: bool = False) -> None:
            """Simplified print method, accepts any objects."""
            # Convert all values to strings like the builtin print
            text = (sep or " ").join(str(v) for v in values) + (end or "\n")
            sys.stdout.write(text)
            if flush:
                sys.stdout.flush()
        
        @staticmethod
        def input(prompt: str, print_method: Optional[Callable[..., Any]] = None) -> str:
            """Simplified input method."""
            if print_method:
                print_method(prompt)
            return input("" if print_method else prompt)
        
        @staticmethod
        def clear() -> None:
            """Simply clears the screen. No ansi, no complexity. Simple and disconnected."""
            os.system("cls" if os.name == "nt" else "clear")
    
    class Color:
        """Represents an ANSI color sequence."""

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
        
        def paint(self, text: str) -> str:
            return self.ansi + text
        
        def reset(self, text: str) -> str:
            return text + self.ansi
        
        def compare(
            self, other: Union["Terminal.Color", str], using: Literal["Tag", "Ansi", "Both"] = "Ansi"
        ) -> bool:
            if isinstance(other, Terminal.Color):
                if using == "Ansi":
                    return self.ansi == other.ansi
                elif using == "Tag":
                    return self.tag == other.tag
                elif using == "Both":
                    return self.ansi == other.ansi and self.tag == other.tag
            elif isinstance(other, str):
                if using == "Ansi":
                    return self.ansi == other
                elif using == "Tag":
                    return self.tag == other
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

        def __add__(
            self, other: Union[str, "Terminal.Color", Iterable[Union[str, "Terminal.Color"]]]
        ) -> "Terminal.Color":
            if isinstance(other, Iterable) and not isinstance(other, (str, bytes)):
                return self.combine(self, *other)
            return self.combine(self, other)

        # enable `Terminal.Color["$gre"]`
        def __class_getitem__(
            cls, key: Union[Tuple[Literal["Tag","ColorKey","Ansi"], str], str]
        ) -> "Terminal.Color":
            if not Terminal._initialized:
                Terminal.colorama_init()

            if isinstance(key, str):
                if key not in Terminal.ColorKeys:
                    raise KeyError(f"Color key {key!r} not found.")
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
    
    class IOString: 
        """I/O string wrapper that can use Terminal print/input methods."""

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
        ) -> None: 
            self.value = Terminal.input(
                *prompt, 
                sep=sep, 
                end=end, 
                flush=flush, 
                color=color, 
                clear_screen=clear_screen, 
                input_text=input_text, 
                n=n
            )

        def print(
            self, 
            *prefix_suffix: str,  
            sep: Optional[str] = " ", 
            end: Optional[str] = "\n", 
            flush: bool = False,
            color: bool = False,
            clear_screen: Union[bool, Tuple[bool, bool]] = False,
        ) -> None:
            before, after = (prefix_suffix + ("", ""))[:2]
            Terminal.print(self, sep=sep, end=end, flush=flush, color=color, clear_screen=clear_screen, prefix=before, suffix=after)
    
    class AnimatedString(IOString): 
        """A string that cycles through multiple frames for animation."""
        def __init__(self, frames: List[str], init: int = 0) -> Self:
            self.frames: List[str] = frames
            self.index: int = init
        
        @property
        def value(self) -> str:
            return self.frames[self.index]
        
        def __str__(self) -> str:
            return self.frames[self.index]
        
        def next(self) -> None:
            """Advance to the next frame, looping around if needed."""
            self.index = (self.index + 1) % len(self.frames)
        
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
        ) -> None:
            """Replace current frame with user input."""
            self.frames[self.index] = Terminal.input(
                *prompt, 
                sep=sep, 
                end=end, 
                flush=flush, 
                color=color, 
                clear_screen=clear_screen, 
                input_text=input_text, 
                n=n
            )

    class ProgressBar(AnimatedString):
        """Animated progress bar that precomputes frames for efficiency."""

        def __init__(self, formatted_string: str, token: str, length: int) -> Self:
            super().__init__([])
            self.formatted_string: str = formatted_string
            self.token: str = token
            self.length: int = length
            self.generate()
        
        def generate(self) -> None:
            """Generate all frames of the progress bar."""
            self.frames = [
                Terminal.progress_bar(self.formatted_string, self.token, self.length, i, self.length)
                for i in range(self.length + 1)
            ]
        
        def calc_index(self, has: int, need: int) -> int:
            "Calculate what index is appropiate for the given corelation."
            return int((has/need) * self.length)

        def set_index(self, index: int) -> None:
            """Set the current frame index."""
            self.index = max(0, min(index, len(self.frames) - 1))
        
        def prev(self) -> None:
            """Move to the previous frame, looping around if needed."""
            self.index = (self.index - 1) % len(self.frames)
        
        def get_frame(self, index: int) -> str:
            """Return a specific frame without changing the current index."""
            return self.frames[index]
        
        def print_frame(
            self, 
            *prefix_suffix: str, 
            index: int = 0,
            sep: Optional[str] = " ", 
            end: Optional[str] = "\n", 
            flush: bool = False,
            color: bool = False,
            clear_screen: Union[bool, Tuple[bool, bool]] = False,
        ) -> None:
            """Print a specific frame with optional prefix/suffix."""
            before, after = (prefix_suffix + ("", ""))[:2]
            Terminal.print(self.frames[index], sep=sep, end=end, flush=flush, color=color, clear_screen=clear_screen, prefix=before, suffix=after)

    @classmethod
    def init(cls) -> None:
        cls.colorama_init()
        cls.regex_init()
    
    @classmethod
    def deinit(cls) -> None:
        cls.colorama_deinit()
        cls.ColorKeys.clear()

    @classmethod
    def colorama_init(cls) -> None:
        if cls._initialized: return
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
    def colorama_deinit(cls) -> None:
        colorama.deinit()
        for color in [
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
        ]: cls.ColorKeys.pop(color.tag)
    
    @classmethod
    def regex_init(cls) -> None:
        cls._regex = re.compile(cls.pattern)
    
    @classmethod
    def new_env(cls, prefix: Optional["Terminal.Color"] = None, suffix: Optional["Terminal.Color"] = None) -> Manager.Environment:
        return cls.manager.new_env(prefix, suffix)
    
    @classmethod
    def set_env_mode(cls, mode: Literal["Single", "Multiple"] = "Single") -> None:
        cls.manager.mode = mode
    
    @overload
    @staticmethod
    def clear(*, ansi: Literal[False] = False) -> None:
        ...
    
    @overload
    @staticmethod
    def clear(*, ansi: Literal[True], flush: bool = True) -> None:
        ...
    
    @staticmethod
    def clear(*, ansi: bool = False, flush: bool = True) -> None:
        """Clears the screen (cross-platform)."""
        if ansi:
            sys.stdout.write("\033[2J\033[H")
            if flush:
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
        color: bool = True, prefix: str = "", suffix: str = ""
    ) -> str:
        """Format values with optional color substitution."""
        if color and not cls._initialized:
            cls.colorama_init()

        suffix = suffix + (end or "")
        text = cls.manager.format((sep or " ").join(map(str, values)))
        if not color:
            return prefix + text + suffix
        
        if not cls._regex:
            cls.regex_init()

        formatted = cls._regex.sub(lambda m: str(cls.ColorKeys.get(m.group(0), m.group(0))), text)
        return prefix + formatted + suffix
    
    @staticmethod
    def progress_bar(
        formatted_string: str = "[had]|[need]|[prog]%",
        token: str = "-", length: int = 10,
        has: float = 0, need: float = 10,
        end: Optional[str] = "", color: bool = True
    ) -> str:
        text = Terminal.format(formatted_string, end=end, color=color)
        factor = has / need if need else 0
        progress = int(length * factor)
        return text.replace("[has]", token * progress).replace("[need]", token * (length - progress)).replace("[prog]", str(int(factor * 100)))
    
    @staticmethod
    def print(
        *values: object,
        sep: Optional[str] = " ",
        end: Optional[str] = "\n",
        flush: bool = False,
        color: bool = False,
        clear_screen: ClearScreenArg = False,
        prefix: str = "",
        suffix: str = "",
    ) -> None:
        """
        Print values to the terminal with optional formatting.

        Supports:
        - Color tags (like $red)
        - Prefix/suffix
        - Screen clearing
        """
        if clear_screen:
            if isinstance(clear_screen, tuple) and clear_screen[0]:
                Terminal.clear(ansi=clear_screen[1], flush=clear_screen[2] if len(clear_screen) > 2 else True)
            elif isinstance(clear_screen, bool):
                Terminal.clear(ansi=False)
        text = Terminal.format(*values, sep=sep, end=end, color=color, prefix=prefix, suffix=suffix)
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
        clear_screen: ClearScreenArg = False,
        input_text: Optional[str] = "",
        n: int = -1
    ) -> str:
        """
        Display a prompt and read user input.

        Supports:
        - Color tags
        - Screen clearing
        - Prefix/suffix through Terminal.print
        - Reading a fixed number of characters via `n`
        """
        if prompt: # We may only use input_text
            Terminal.print(*prompt, sep=sep, end=end, flush=flush, color=color, clear_screen=clear_screen)
        if n == -1:
            return input(input_text or "")
        return sys.stdin.read(n)
    
    @classmethod
    def set_color(cls, color: "Terminal.Color") -> None:
        """Immediately set console color without newline."""
        sys.stdout.write(str(color))
        sys.stdout.flush()
    
    @staticmethod
    def log(level: str, *msg, color=True):
        prefix = f"[{level.upper()}]"
        if color:
            prefix = {
                "INFO": "$blu",
                "WARN": "$yel",
                "ERROR": "$red"
            }.get(level.upper(), "") + prefix + "$res"
        Terminal.print(prefix, *msg, color=color)
    
    @staticmethod
    def space() -> None:
        """Simple print a space in the terminal."""
        Terminal.Simple.space()