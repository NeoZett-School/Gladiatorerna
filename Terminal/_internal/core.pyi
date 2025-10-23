"""
The core features for the terminal.
"""

from typing import Iterable, Tuple, List, Dict, Optional, Callable, Literal, Union, Self, TypeVar, Any, overload
from .enums import Mode
import re

T = TypeVar("T", bound="Terminal.Color")
ClearScreenArg = Union[bool, Tuple[bool, bool], Tuple[bool, bool, bool]]

class History:
    formattings: List[str]
    inputs: List[str]

class Manager:
    """The manager handles terminal environments."""

    env_stack: List[Manager.Environment]
    mode: Mode

    class Environment:
        """An environment contain vital details and schematics for your terminal."""

        manager: Manager
        prefix_color: Optional[Terminal.Color]
        suffix_color: Optional[Terminal.Color]
        active: bool
        formatted: List[str]

        class GlobalInterface:
            """Public interface for an active environment context."""

            def __init__(self, env: "Manager.Environment") -> Self:
                ...
            
            @property
            def active(self) -> bool:
                """Wheter this environment is active."""
                ...
            
            @property
            def prefix(self) -> "Terminal.Color":
                """The prefix color."""
                ...
            
            @property
            def suffix(self) -> "Terminal.Color":
                """The suffix color."""
                ...
            
            @property
            def formatted(self) -> List[str]:
                """A list of all formatted strings."""
                ...
            
            def format(self, text: str) -> str:
                """Format a text."""
                ...
            
            def disable(self) -> None:
                """Disable this environment."""
                ...
            
            def reset(self) -> None:
                """Reset this environment."""
                ...
        
        def __init__(
            self, 
            manager: "Manager", 
            prefix: Optional["Terminal.Color"] = None, 
            suffix: Optional["Terminal.Color"] = None
        ) -> Self: ...

        @property
        def prefix(self) -> str:
            """The prefix in ansi characters."""
            ...
        
        @property
        def suffix(self) -> str:
            """The suffix in ansi characters."""
            ...
        
        def enable(self) -> GlobalInterface:
            """Enable this environment."""
            ...
        
        def disable(self) -> None:
            """Disable this environment."""
            ...
        
        def __enter__(self) -> GlobalInterface:
            ...
        
        def __exit__(self, *args) -> None:
            ...
        
        def format(self, text: str) -> str:
            """Format a text."""
            ...
        
        def reset(self) -> None:
            """Reset this environment."""
            ...
    
    def __init__(self) -> Self:
        ...
    
    @property
    def active(self) -> bool:
        """Wheter this manager is active."""
        ...
    
    def disable(self) -> None:
        """Disable all active environments."""
        ...
    
    def format(self, text: str) -> str:
        """Apply formatting from environments. (Depends on mode)"""
        ...
    
    def new_env(self, prefix: Optional["Terminal.Color"] = None, suffix: Optional["Terminal.Color"] = None) -> Environment:
        """Create a new environment."""
        ...

class Terminal:
    """A flexible terminal interface with colors, formatting, and environment stacks."""

    ColorKeys: Dict[str, "Terminal.Color"]
    manager: Manager
    pattern: str
    _initialized: bool
    _regex: Optional[re.Pattern]

    class Simple:
        """Disconnected, minimal terminal I/O."""

        @staticmethod
        def space() -> None:
            """Simply print a space in the terminal."""
            ...
        
        @staticmethod
        def print(*values: object, sep: Optional[str] = " ", end: Optional[str] = "\n", flush: bool = False) -> None:
            """Simplified print method, accepts any objects."""
            ...
        
        @overload
        @staticmethod
        def input(prompt: object = "", /) -> str:
            """Simplified input method."""
            ...
        
        @overload
        @staticmethod
        def input(prompt: object = "", print_method: Optional[Callable[..., Any]] = None) -> str:
            """Simplified input method."""
            ...
        
        @staticmethod
        def clear() -> None:
            """Simply clears the screen. No ansi, no complexity. Simple and disconnected."""
            ...
    
    class Color:
        """Represents an ANSI color sequence."""

        ansi: str
        tag: Optional[str]

        def __init__(self, *ansi: str, tag: Optional[str] = None) -> Self:
            ...

        @classmethod
        def lookup(cls, tag: str) -> Optional["Terminal.Color"]:
            """Lookup a color tag."""
            ...
        
        @classmethod
        def rgb(cls, r: int, g: int, b: int) -> "Terminal.Color":
            """Retrieve a color with the given rgb."""
            ...
        
        @classmethod
        def bg_rgb(cls, r: int, g: int, b: int) -> "Terminal.Color":
            """Retrieve a color with the given rgb as background."""
            ...
        
        def paint(self, text: str) -> str:
            """Paint the given text."""
            ...
        
        def reset(self, text: str) -> str:
            """Reset the given text."""
            ...
        
        def compare(
            self, other: Union["Terminal.Color", str], using: Literal["Tag", "Ansi", "Both"] = "Ansi"
        ) -> bool: 
            """Compare this with another color."""
            ...

        @classmethod
        def combine(cls, *colors_or_strings: Union["Terminal.Color", str]) -> "Terminal.Color":
            """Combine multiple colors or strings into a single Color object."""
            ...
        
        def __str__(self) -> str:
            ...
        
        def __repr__(self) -> str:
            ...
        
        def __eq__(self, other: object) -> bool:
            ...
        
        def __add__(
            self, other: Union[str, "Terminal.Color", Iterable[Union[str, "Terminal.Color"]]]
        ) -> "Terminal.Color": ...

        def __class_getitem__(
            cls, key: Union[Tuple[Literal["Tag","ColorKey","Ansi"], str], str]
        ) -> "Terminal.Color": ...
    
    class IOString: 
        """I/O string wrapper that can use Terminal print/input methods."""

        value: str

        def __init__(self, value: str = "") -> Self:
            ...
        
        def __str__(self) -> str:
            ...
        
        def clear(self) -> None:
            """Clear the IO string."""
            ...
        
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
            """Change the value from user input."""
            ...

        def print(
            self, 
            *prefix_suffix: str,  
            sep: Optional[str] = " ", 
            end: Optional[str] = "\n", 
            flush: bool = False,
            color: bool = False,
            clear_screen: Union[bool, Tuple[bool, bool]] = False,
        ) -> None: 
            """Print the value."""
            ...
    
    class AnimatedString(IOString):
        """A string that cycles through multiple frames for animation."""

        frames: List[str]
        index: int

        def __init__(self, frames: List[str], init: int = 0) -> Self:
            ...
        
        @property
        def value(self) -> str:
            """The current frame."""
            ...
        
        def __str__(self) -> str:
            ...
        
        def set_index(self, index: int) -> None:
            """Set the current frame index."""
            ...
        
        def next(self) -> None:
            """Advance to the next frame, looping around if needed."""
            ...
        
        def prev(self) -> None:
            """Move to the previous frame, looping around if needed."""
            ...
        
        def get_frame(self, index: int) -> str:
            """Return a specific frame without changing the current index."""
            ...
        
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
            ...
        
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
            ...
        
        def clear(self) -> None:
            """Clear the current frame."""
            ...
    
    class ProgressBar(AnimatedString):
        """Animated progress bar that precomputes frames for efficiency."""

        formatted_string: str
        token: str
        length: int

        def __init__(self, formatted_string: str, token: str, length: int) -> Self:
            ...
        
        def generate(self) -> None:
            """Generate all frames of the progress bar."""
            ...
        
        def calc_index(self, has: int, need: int) -> int:
            "Calculate what index is appropiate for the given corelation."
            ...
    
    @classmethod
    def init(cls) -> None:
        """Initiate the terminal."""
        ...
    
    @classmethod
    def deinit(cls) -> None:
        """Deinitiate the terminal."""
        ...
    
    @classmethod
    def colorama_init(cls) -> None:
        """Initiate the colorama module and load all colors. [See `init`]"""
        ...
    
    @classmethod
    def colorama_deinit(cls) -> None:
        """Deinitate the colorama module and unload all colors. [See `deinit`]"""
        ...
    
    @classmethod
    def regex_init(cls) -> None:
        """Initiate the regex-pattern. [See `init`]"""
        ...
    
    @classmethod
    def new_env(cls, prefix: Optional[Color] = None, suffix: Optional[Color] = None) -> Manager.Environment:
        """Create a new environment."""
        ...
    
    @classmethod
    def set_env_mode(cls, mode: Union[Mode, Literal["Single", "Multiple"]] = Mode.SINGLE) -> None:
        """Set the environment mode (Single or Multiple). This affects how colors are rendered."""
        ...
    
    @overload
    @staticmethod
    def clear(*, ansi: Literal[False] = False) -> None:
        """Clear the console like normal. (The same: `Simple.clear`)"""
        ...
    
    @overload
    @staticmethod
    def clear(*, ansi: Literal[True], flush: bool = True) -> None:
        """Clear the console using ansi codes. May not work as expected. More compatible."""
        ...
    
    @classmethod
    def lookup(cls, tag: str) -> Optional[Color]:
        """Lookup a color tag."""
        ...
    
    @classmethod
    def rgb(cls, r: int, g: int, b: int) -> Color:
        """Retrieve a color with the given rgb."""
        ...
    
    @classmethod
    def bg_rgb(cls, r: int, g: int, b: int) -> Color:
        """Retrieve a color with the given rgb as background."""
        ...
    
    @overload
    @classmethod
    def add_color(cls, color: Color, /) -> None:
        """Add a new color. Optionally, specify the tag."""
        ...
    
    @overload
    @classmethod
    def add_color(cls, color: Color, tag: Optional[str] = None) -> None:
        """Add a new color. Optionally, specify the tag."""
        ...
    
    @overload
    @classmethod
    def pop_color(cls, tag: str, /) -> str:
        """Pop a color by the given tag."""
        ...
    
    @overload
    @classmethod
    def pop_color(cls, tag: str, default: Optional[Color], /) -> str:
        """Pop a color by the given tag. Provide a default in case the tag cant be found."""
        ...
    
    @classmethod
    def format(
        cls, *values: object,
        sep: Optional[str] = " ", end: Optional[str] = "",
        color: bool = True, prefix: str = "", suffix: str = ""
    ) -> str:
        """Format values with optional color substitution."""
        ...
    
    @staticmethod
    def progress_bar(
        formatted_string: str = "[had]|[need]|[prog]%",
        token: str = "-", length: int = 10,
        has: float = 0, need: float = 10,
        end: Optional[str] = "", color: bool = True
    ) -> str:
        """Build a new progress bar."""
        ...
    
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
        ...
    
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
        ...
    
    @classmethod
    def set_color(cls, color: Color) -> None:
        """Immediately set console color without newline."""
        ...
    
    @staticmethod
    def log(level: Literal["INFO", "WARN", "ERROR"], *msg: object, color: bool = True) -> None:
        """Log message with a provided level."""
        ...
    
    @staticmethod
    def space() -> None:
        """Simply print a space in the terminal."""
        ...