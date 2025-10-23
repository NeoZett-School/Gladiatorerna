from typing import Type, Optional, Union, Literal, overload
from ._internal import Builder as _Builder, FileSystem as _FileSystem, Terminal as _Terminal, Mode as _Mode
from ._internal.core import History as _History, Manager, ClearScreenArg

Mode: Type[_Mode]
Terminal: Type[_Terminal]
Simple: Type[_Terminal.Simple]
History: Type[_History]
Builder: Type[_Builder]
FileSystem: Type[_FileSystem]

manager: Manager

def terminal_init() -> None: 
    """Initialize the terminal."""
    ...
def terminal_deinit() -> None: 
    """Deinitialize the terminal."""
    ...

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

def space() -> None:
    """Simply print a space in the terminal."""
    ...

@overload
def clear(*, ansi: Literal[False] = False) -> None:
    """Clear the console like normal. (The same: `Simple.clear`)"""
    ...

@overload
def clear(*, ansi: Literal[True], flush: bool = True) -> None:
    """Clear the console using ansi codes. May not work as expected. More compatible."""
    ...

def lookup(tag: str) -> Optional[_Terminal.Color]:
    """Lookup a color tag."""
    ...

def log(level: Literal["INFO", "WARN", "ERROR"], *msg: object, color: bool = True) -> None:
    """Log message with a provided level."""
    ...

def new_env(prefix: Optional[_Terminal.Color] = None, suffix: Optional[_Terminal.Color] = None) -> Manager.Environment:
    """Create a new environment."""
    ...

def set_env_mode(mode: Union[_Mode, str] = Mode.SINGLE) -> None:
    """Set the environment mode (Single or Multiple). This affects how colors are rendered."""
    ...

def progress_bar(
    formatted_string: str = "[had]|[need]|[prog]%",
    token: str = "-", length: int = 10,
    has: float = 0, need: float = 10,
    end: Optional[str] = "", color: bool = True
) -> str:
    """Build a new progress bar."""
    ...

IOString: Type[_Terminal.IOString]
AnimatedString: Type[_Terminal.AnimatedString]
ProgressBar: Type[_Terminal.ProgressBar]